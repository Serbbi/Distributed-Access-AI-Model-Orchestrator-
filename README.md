# Scalable Computing 2024-2025

# Introduction

This project, done in collaboration with TNO, focuses on distributed access control for models and time series data, as part of Project Zefes.  Managing and securing access to sensitive datasets has become more difficult, especially across the cloud. To address this, we integrate open source and distributed authentication and authorization tools as well as distributed time series databases in order to enhance modern industries driven by data.

# Project Goal & Scope

To successfully create our  system, we had a set of key goals which needed to be achieved so that our system would be considered successful. In addition to these goals, our collaboration with TNO introduced several additional requirements which further guided our project.

**Project Goal**  
Create an Auth-Enabled multi-user application with which users are able to upload machine learning models using python source code alongside the associated data. The application should ensure that the users are able to view their uploaded data and models as well as run them with the given data as input. The output of any user models should be displayed to the user.

**Technical Goals**  
Given our project’s involvement with TNO, we must ensure that our requirements reflect their expectations. As such we have added an associated type to each technical goal to make the domain of each goal explicit. 

1. **Goal**: Have the frontend act as the single point of ingress into the application.  
   **Goal Type: System Goal**  
   **Explanation**:  To ensure that our system is secure we only want to have 1 point of ingress into the application itself. Users should only be able to access the frontend through which all application functionality should be available (given the correct permissions). Any admin related tasks can be executed through SSH access directly into the VM, as exposing endpoints which handle key system functionality is not secure.

2. **Goal**: The application must have an Auth layer which oversees all authentication and authorization. The authentication & authorization should be created using the open-source solutions: Ory Kratos & Ory Keto.  
   **Goal Type: TNO System Goal**  
   **Explanation**: To ensure the system is able to be deployed on the filtered network to be demo-ed to TNO would require us to have proper authentication enabled within the system. Additionally, as part of the TNO requirements a permission system is expected. However to implement this we also need to have associated user accounts and session management requiring an integrated permission system.

3. **Goal**: Allow for users to upload and run their python machine learning models asynchronously in a scalable way and have their output returned to them.  
   **Goal Type: System Goal**  
   Explanation: The main algorithm of our program is the orchestration of machine learning models and thereby is mentioned as a separate goal. The orchestration should be location aware (explained later in its own goal) as well as asynchronously communicate output to the user which started the process.

4. **Goal**:  The system should store both the data and model with specific support for time series data.  
   **Goal Type: System Goal**  
   **Explanation**: Our system needs to store the machine learning models and associated data. This is a given, however in combination with Goal 5, TNO requires our system to explicitly support time series data storage in a scalable way.

5. **Goal**: The user permissions should allow for fine-grain access to specific sections of time series data.  
   **Goal Type: TNO System Goal**  
   **Explanation**: As part of the collaboration with TNO, we are investigating how to integrate a permissions system with fine-grained time series data access. This means although the entire time-series data exists within the database, it should be possible for specific users to be prevented from accessing specific portions of time series data.

6. **Goal**: The system should be deployed in a cloud environment.  
   **Goal Type: System Goal**  
   **Explanation**: To ensure a scalable, maintainable, and extensible approach, our system needs to be deployed in a cloud environment. A cloud deployment also enables us to leverage the high availability of compute, network, and memory resources provided by Habrok through Openstack, also reducing the overhead of manually maintaining the infrastructure. 

7. **Goal**: The system as well as the cloud environment should be deployed automatically through the use of pipelines.  
   **Goal Type: System Goal**  
   **Explanation**: Due to the need for deployment efficiency, reproducibility, and consistency, our system must be deployed through the use of automated pipelines, specifically the automated pipelines provided by GitLab, where our project files are currently hosted. Deploying through automated pipelines also provides the added benefit of enabling faster rollouts of features.   
     
8. **Goal**: The machine learning model orchestration needs to be location aware.  
   **Goal Type: System Goal**  
   **Explanation:** The system must ensure that model training occurs on the same node where the data is stored. This prevents unnecessary data transfers between nodes, reducing both network and computing overhead. By deploying the orchestrator alongside the data, our system demonstrates data location awareness.

**Scope**  
The project has 2 key elements which need to be implemented for it to be considered a technical success. These 2 goals are referred to as *primary goals* are the main focus for the project with the other technical goals acting as supplementary goals. 

1. Ensure the machine learning model orchestration is location aware.

2. Ensure time series data has fine-grain permission based access control support.

With the exception of the aforementioned primary goals, the rest of the technical goals have several limitations to ensure that the timeline for our project remains feasible.

1. **Auth System Limitations** \- Since our application is serving as a demo rather than a deployable solution, we will take a shortcut by seeding the Auth service with permissions and user accounts. This means that the creation of new users will not be possible directly through user registration in the frontend and enable us to focus on permissions for *existing* users. It is important to mention that although we will seed Ory Keto with permissions, these will be extensible during run-time, but will not have fine-grain management built in; our system is not a permission management solution and therefore will not have any UI or logic for fine-grain control (e.g. managing user organizations). 

2. **Data Storage Limitations** \- We are assuming that all python models provided are directly compatible with our orchestration service; they are able to be compiled and run by our selected python run-time solution. This means that we will not be taking into account any issues which may arise from improperly coded or non-version managed code. Additionally, we assume all data provided will be time series data and directly compatible with the user’s machine learning model. Furthermore, we assume that the time series data can be parsed in a way that allows us to extract the headers and each data value for every time step. 

# Architecture

The system as whole is hosted on multiple instances of virtual machines in a cloud environment provided by OpenStack. We utilize a thin-client model, offloading all critical processing to the backend systems. The constituent components are explained in more depth in this section.  

![System architecture image](./images/architecture.png)

## Frontend

The tech stack of the frontend consists of React, NextJs, Shadcn and Typescript. This combination of technologies was chosen because of our familiarity working with them, as well as the high number of available resources for them online.   
The frontend is implemented as a thin client \- it offloads all processing to the backend through a series of API calls to ensure that the user’s experience is not handicapped by their system’s performance characteristics. By relying on this approach we leverage one of the advantages of cloud systems: the elastic scalability, allowing the system to scale through replication when needed.  
The frontend itself has several key tasks, firstly it must enable the user to login and validate their session to gain access to the protected functionality, which in this case is access to the model and data through the API. This is done by establishing a session cookie through direct communication with Ory Kratos within the Auth layer. Once this cookie is established it is then passed as a header to every request to the backend which then validates it and its associated permissions.  
Finally, the frontend also establishes a websocket with the backend to ensure it is able to receive updates regarding the jobs they have run asynchronously.

## Backend

The backend of the system is also responsible for ensuring users can only access authorized resources and only when authorized to do this. This is done through integration with the Auth layer, however the backend is responsible for actually enforcing the permissions. For every HTTP request the backend receives to a protected route or resource, the session cookie *must* be attached as a header. The backend then checks whether the session is valid, and at the same time isolates the user ID from the request. Once the session has been confirmed by the Auth Layer, the backend then queries all associated permissions for a given user for the desired resource to determine whether the action is granted or denied. 

## Auth Layer

The Auth Layer is a critical component of the system because it oversees 2 important functionalities: authentication and authorization. Given the goals mentioned in previous sections, Ory Kratos was used as our identity provider. It is directly responsible for storing users according to the defined schema (for simplicity our implementation only required an email and password to create a user instance). All interactions with Ory Kratos occur through their built in HTTP request based API. It is important to mention that Ory Kratos, interacts directly with both the frontend and backend services, as they both require direct user authorization.   
In contrast, user authorization is implemented using Ory Keto and only interacts with the backend. The frontend does not need explicit knowledge of what is allowed, rather it only needs to know whether data is returned or not. Thereby, encapsulating the permission checks within the backend allows for a more robust flow. Ory Keto, is similar to Ory Kratos in the sense that all interactions happen through their HTTP request based API, but there is no direct integration between the two. This means that the users are not directly synched and need additional backend logic to do so.  
Finally, the Auth layer also consists of a postgres database which is directly integrated with Ory Kratos to store user accounts. In contrast, Ory Keto does not use this database, relying only on in memory storage. In a production scenario this would not be ideal as it could very quickly result in high memory usage, but for the purposes of this application we decided this was sufficient.

## TSDB

The time-series database used is Cassandra, due to its distributed storage system as well as its ease of integration with authorization models. We used a base Cassandra helm chart, which also provided the added benefit of out-of-the-box partitioning of the dataset across the many nodes that we have in the infrastructure. The schema of our time-series data includes:

- **timestamp**, which is the partition key  
- **country**, which is the clustering key  
- **resourceId**, which is used for user authorization of particular data  
- two integer **value**s, which are used in the model training

The first 2 fields, mainly the timestamp and the country, make up the primary key.

## MinIO

MinIO is an object storage system, capable of working with unstructured data such as images, videos, backups etc. In our application, we use MinIO to store the trained models and other output (plots, graphs etc.) received after running the orchestrator. After a model is trained, the output objects are only accessible by users from the same organization, this is done using the MinIO buckets corresponding to tokens generated by Ory Keto.

## Orchestrator

This part of the system is responsible for training models. It takes as input a ZIP file containing the code to train a model and the data used for training. The zip file comes directly from the user and the data is provided by the backend after checking the permissions of the user to use that data. The orchestrator is spawning a docker container and pasting the code and data into it. After the training is done, the orchestrator will extract the output directory from the container and send it back to the backend which in turn will save it to MinIO. Terraform \- Amr  
We use Terraform to provision the VMs and consequently the infrastructure. We have 2 different configurations for 2 different sets of VMs, where we have a master VM and a worker VM. Both of these have different configurations. Both configurations rely on Ubuntu version 22.04 as this image is most familiar to us. We specifically set up 1 master instance, and 3 worker instances, where the master has 50 GB worth of storage configured with it, and the workers each have 20 GBs. We also have managed to set up the networking between these instances, as well the master instance and the outside.

## Pipeline

There are 2 pipelines within our project:

* IaC Pipeline: Deploys our infrastructure through the [Terraform](#heading=h.q46088kea9wc) code provided.  
* Deployment Pipeline: Deploys our main application into the infrastructure( i.e the frontend, backend, orchestrator, auth layers, and databases discussed above).

For the IaC pipeline, we rely on a template, which is provided by GitLab for deploying infrastructure by using terraform. The IaC pipeline ensures correctness and readable syntax of the terraform files. Following this is the creation of an execution plan, which lets us preview changes to be made. We also ensure that we have the latest terraform state as well as comparing with the previous state to show any differences between this plan and the previous plan (if any). Then, we deploy the infrastructure proposed in the plan to the University of Groningen’s Habrok Cluster. Next, we extract the ip address of the VM that is exposed to the outside, and add it to the GitLab CI/CD variables store for later use.  Ultimately, since we have set up a GitLab Agent to be able to deploy into our Kubernetes cluster, we wait for the agent to be running to ensure that the deployment is successful, and that we are able to proceed to the next pipeline. We also have a final stage set up for cleaning that is triggered manually when needed to redeploy from scratch. 

The deployment pipeline  starts off with building the docker images of the backend, frontend, orchestrator. Then, it creates the secrets necessary for helm to be able to run the images. After that, helm deploys the application with the secrets created as well as the other configurations such as number of replicas. We also have a final stage setup for removing everything deployed by helm in the case of a needed refresh.

# Implementation & Key Decisions 

One of the primary objectives of this project was to identify and integrate a suitable time-series database into our application. We evaluated several options, including `Timescale`, `InfluxDB`, and `PostgreSQL`, but ultimately decided to go with `Apache Cassandra`. 

`Apache Cassandra` met all of our requirements having built-in partitioning and distribution across nodes, ensuring better location awareness of data. As a fully open-source solution, Cassandra allows for seamless horizontal scaling across all nodes in the cluster, making it an ideal choice for our application.

The orchestrator's code and core logic were adapted from a project in the Cloud Computing course and modified to fit our needs. Initially, the orchestrator took as input bash code scripts, ran them inside containers and returned the corresponding output. The main modification involved changing the input handling to process a ZIP file instead of a code string and copying that into the spawned container. Due to the relatively long time to train a model, it was also necessary to adjust the time that RabbitMQ checks for heartbeats so that the connection between components would not time out.

# Work Distribution & Collaboration

| Report |  |  |
| :---- | :---- | :---- |
| Group Member | Task | Notes |
| Aras & Amr | Project Goal & Scope |  |
| Aras | Frontend, Auth Layer & Backend |  |
| Aras, Amr, Serban | Document review and project coordination |  |
| **Code** |  |  |
| Group Member | Task | Notes |
| Aras | Frontend |  |
| Aras | Ory Kratos & Ory Keto |  |
| Aras | Backend Auth Management |  |
| Aras, Amr, Serban | System Architecture | The group as a whole invested a lot of time into key design decisions for the system. |
| Amr & Serban | Infrastructure and Pipeline | Amr wrote the IaC pipeline mainly that deploys the provisioned VMs. Serban and Amr worked together on deploying the application itself into the infrastructure through pipelines.  |
| Serban | Orchestrator |  |
| Serban | MinIO |  |
| Serban | Time-series DB |  |

### Swagger

```
http://localhost:8080/swagger-ui/index.html
```

### Based
```
sudo chmod 644 /etc/rancher/k3s/k3s.yaml && export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
```
