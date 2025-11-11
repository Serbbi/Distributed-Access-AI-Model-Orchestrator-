import logging
import time
import threading
import sys
import os
import signal
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from kubernetes.watch import Watch
from kubernetes.stream import stream
from .consumer import NewCodeBlockMessage, MessageConsumer
from .producer import MessageProducer, LogMessage, MetaData
from .rabbit_config import RabbitConfig
import base64
import tempfile
import zipfile

logger = logging.getLogger(__name__)

def get_current_time():
    return int(time.time() * 1000)

class MessageService:
    def __init__(self, message_producer: MessageProducer):
        self.message_producer = message_producer
        self.timeout = int(os.getenv("TIMEOUT", 1000))
        self.active_jobs = set()
        
        # Load Kubernetes config
        try:
            config.load_incluster_config()  # For running inside cluster
        except:
            config.load_kube_config()  # For local development
            
        self.batch_api = client.BatchV1Api()
        self.core_api = client.CoreV1Api()
        
        signal.signal(signal.SIGTERM, self.sigterm_handler)
        signal.signal(signal.SIGINT, self.sigterm_handler)
        signal.signal(signal.SIGQUIT, self.sigterm_handler)


    def sigterm_handler(self, signo, _stack_frame):
        """Clean up running jobs on termination"""
        logger.info(f"Received signal {signo}, cleaning up jobs")
        for job_name in list(self.active_jobs):
            try:
                self.batch_api.delete_namespaced_job(
                    name=job_name,
                    namespace="default",
                    propagation_policy="Background"
                )
                logger.info(f"Cleaned up job: {job_name}")
            except Exception as e:
                logger.error(f"Error cleaning up job {job_name}: {e}")
        sys.exit(0)

    def send_update_message(self, message, content, start_time, status, exit_code):
        metadata = MetaData(
            id=message.id,
            start=start_time,
            end=get_current_time(),
            duration=int(get_current_time() - start_time),
            status=status,
            exitCode=exit_code
        )
        log_message = LogMessage(id=message.id, content=content, metadata=metadata)
        self.message_producer.send_message(log_message)

    def get_pod_ip_node_mapping(self, namespace="default"):
        try:
            # Load in-cluster config
            config.load_incluster_config()
        except config.ConfigException:
            raise RuntimeError("This script must run inside a Kubernetes pod with access permissions.")

        v1 = client.CoreV1Api()
        ip_to_node = {}

        try:
            pods = v1.list_namespaced_pod(namespace)
            for pod in pods.items:
                ip = pod.status.pod_ip
                node = pod.spec.node_name
                name = pod.metadata.name
                if ip:
                    ip_to_node[ip] = {"pod": name, "node": node}

        except ApiException as e:
            logger.error("Exception when calling CoreV1Api->list_namespaced_pod: %s\n" % e)

        return ip_to_node

    def _get_output_files(self, pod_name, output_path='/code/output'):
        """Retrieve output files from job pod"""
        try:
            # Create tar archive and base64 encode in one command
            tar_command = [
                'sh', '-c',
                f'cd {output_path} && '
                'tar -czf - . | '  # Create tar and output to stdout
                'base64 -w 0'      # Encode without line breaks
            ]

            resp = stream(
                self.core_api.connect_get_namespaced_pod_exec,
                pod_name,
                'default',
                command=tar_command,
                stderr=True,
                stdin=False,
                stdout=True,
                tty=False,
                _preload_content=False
            )
            
            # Capture output
            encoded_data = ""
            while resp.is_open():
                resp.update(timeout=5)
                if resp.peek_stdout():
                    encoded_data += resp.read_stdout()
                if resp.peek_stderr():
                    logger.error(f"Tar error: {resp.read_stderr()}")
            
            if not encoded_data:
                logger.error("No data received from pod")
                return None
                
            logger.info(f"Received {len(encoded_data)} characters of encoded data")
            return encoded_data
                
        except Exception as e:
            logger.error(f"Error retrieving output files for pod {pod_name}: {str(e)}")
            return None

    def _create_job_manifest(self, message, job_name, node_name):
        """Create a Kubernetes Job manifest"""
        main_py_content = ""
        requirements_content = ""
        time_series_data_content = ""

        decoded_data = base64.b64decode(message.code)
        with tempfile.NamedTemporaryFile(suffix='.zip') as tmp_zip:
            tmp_zip.write(decoded_data)
            tmp_zip.flush()
            
            # Extract ZIP to temporary directory
            with tempfile.TemporaryDirectory() as tmp_dir:
                with zipfile.ZipFile(tmp_zip.name, 'r') as zip_ref:
                    zip_ref.extractall(tmp_dir)
                
                # Put extracted files into container
                for root, _, files in os.walk(tmp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r') as f:
                            if file == "main.py":
                                main_py_content = f.read()
                            elif file == "requirements.txt":
                                requirements_content = f.read()
                            elif file == "time_series_data.csv":
                                time_series_data_content = f.read()
        
        # Create a ConfigMap for the code and requirements
        configmap = client.V1ConfigMap(
            metadata=client.V1ObjectMeta(name=f"{job_name}-code"),
            data={
                "main.py": main_py_content,
                "requirements.txt": requirements_content,
                "time_series_data.csv": time_series_data_content
            }
        )
        
        try:
            self.core_api.create_namespaced_config_map(
                namespace="default",
                body=configmap
            )
        except ApiException as e:
            logger.error(f"Failed to create ConfigMap: {e}")
            raise

        # Job manifest
        return client.V1Job(
            metadata=client.V1ObjectMeta(name=job_name),
            spec=client.V1JobSpec(
                template=client.V1PodTemplateSpec(
                    spec=client.V1PodSpec(
                        node_name=node_name,
                        containers=[
                            client.V1Container(
                                name="job-container",
                                image="python:3.10-slim",
                                command=["/bin/sh", "-c"],
                                args=[
                                    "cd code && ls && pip install -r requirements.txt && python main.py && echo JOB_COMPLETED && sleep 300"
                                ],
                                volume_mounts=[
                                    client.V1VolumeMount(
                                        name="code-volume",
                                        mount_path="/code"
                                    ),
                                    client.V1VolumeMount(
                                        name="output-volume",
                                        mount_path="/code/output"
                                    )
                                ]
                            )
                        ],
                        termination_grace_period_seconds=600,
                        volumes=[
                            client.V1Volume(
                                name="code-volume",
                                config_map=client.V1ConfigMapVolumeSource(
                                    name=f"{job_name}-code"
                                )
                            ),
                            client.V1Volume(
                                name="output-volume",
                                empty_dir={}
                            )
                        ],
                        restart_policy="Never"
                    )
                ),
                backoff_limit=0,
                ttl_seconds_after_finished=300  # Clean up 5 minutes after completion
            )
        )

    def _run_code_in_k8s(self, message, start_time, ch, delivery_tag):
        ip_to_node = self.get_pod_ip_node_mapping("default")
        pod_node = ip_to_node.get(message.cassandra_pod_ip)
        node_name = pod_node["node"] if pod_node else None
        logger.info(f"Node name: {node_name}")

        try:
            ch.basic_ack(delivery_tag=delivery_tag)
            job_name = f"code-job-{message.id}"
            self.active_jobs.add(job_name) 

            # Create the Job
            job_manifest = self._create_job_manifest(message, job_name, node_name)
            self.batch_api.create_namespaced_job(
                namespace="default",
                body=job_manifest
            )
            logger.info(f"Created Kubernetes job: {job_name}")
            
            self.send_update_message(message, '', start_time, "RUNNING", None)
            

            # Wait for job to start
            while True:
                job = self.batch_api.read_namespaced_job(
                    name=job_name,
                    namespace="default"
                )
                if job.status.active:
                    logger.info(f"Job {job_name} is active")
                    time.sleep(10)
                    break
                time.sleep(1)


            pods = self.core_api.list_namespaced_pod(
                namespace="default",
                label_selector=f"job-name={job_name}"
            )

            watch = Watch()

            if pods.items:
                pod_name = pods.items[0].metadata.name
                logger.info(f"Pod {pod_name} is running")

                # Monitor job status
                for log_line in watch.stream(
                    self.core_api.read_namespaced_pod_log,
                    name=pod_name,
                    namespace="default",
                    follow=True
                ):
                    if "JOB_COMPLETED" in log_line:
                        logger.info("JOB COMPELTED successfully")
                        break
    
            else:
                logger.error(f"No pods found for job {job_name}")
            
            # Get job logs
            output = ""
            if pods.items:
                pod_name = pods.items[0].metadata.name
                logs = self.core_api.read_namespaced_pod_log(
                    name=pod_name,
                    namespace="default"
                )
                output = logs
            
            # Get output files
            output_files = self._get_output_files(pods.items[0].metadata.name)
            if output_files:
                logger.info(f"Output files for job {job_name} retrieved successfully")

            # Determine exit code
            exit_code = 0
            if job.status.failed:
                exit_code = 1
            
            self.send_update_message(message, output, start_time, 
                                   "SUCCESS" if exit_code == 0 else "FAILURE", 
                                   exit_code)
            
        except Exception as e:
            logger.error(f"Error executing code in Kubernetes: {e}")
            self.send_update_message(message, str(e), start_time, "FAILURE", 1)
        finally:
            self.active_jobs.remove(job_name)
            # Clean up
            try:
                self.batch_api.delete_namespaced_job(
                    name=job_name,
                    namespace="default",
                    propagation_policy="Background"
                )
                self.core_api.delete_namespaced_config_map(
                    name=f"{job_name}-code",
                    namespace="default"
                )
            except Exception as e:
                logger.error(f"Error cleaning up resources: {e}")

    def handle_in_k8s(self, message: NewCodeBlockMessage, ch, delivery_tag):
        logger.debug(f"Handling message in Kubernetes: {message.id}")
        start_time = get_current_time()
        
        # Run the code in a separate thread
        self.exec_thread = threading.Thread(
            target=self._run_code_in_k8s,
            args=(message, start_time, ch, delivery_tag)
        )
        self.exec_thread.start()
        
        # Wait for the thread to finish or timeout
        self.exec_thread.join(timeout=self.timeout)
        
        if self.exec_thread.is_alive():
            logger.warning(f"Execution exceeded timeout for job {message.id}")
            self.send_update_message(message, '', start_time, "TIMEOUT", -1)

    def handle(self, message: NewCodeBlockMessage, ch, delivery_tag):
        logger.info(f"Handling message: {message.id}")
        self.handle_in_k8s(message, ch, delivery_tag)

def start_handling_messages():
    config = RabbitConfig()
    message_producer = MessageProducer(config)
    logger.info("Successfully done the message producer")

    message_service = MessageService(message_producer)
    logger.info("Successfully done the message service")

    message_consumer = MessageConsumer(config, message_service)
    logger.info("Successfully done the message consumer, starting to consume messages")
    message_consumer.start_consuming()