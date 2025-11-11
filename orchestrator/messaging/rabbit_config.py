#!/usr/bin/env python
import pika
from .consumer import NewCodeBlockMessage
import logging
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()  # take environment variables from .env.


class RabbitConfig:
    # load environment variables
    CODE_QUEUE_NAME=os.getenv("CODE_QUEUE_NAME")
    LOGS_ROUTING_KEY=os.getenv("LOGS_ROUTING_KEY")
    LOGS_EXCHANGE=os.getenv("LOGS_EXCHANGE")
    CODE_BLOCKS_EXCHANGE=os.getenv("CODE_BLOCKS_EXCHANGE")
    
    host = os.getenv("SPRING_RABBITMQ_HOST")
    port = os.getenv("RABBIT_MQ_PORT")
    virtual_host = os.getenv("RABBIT_MQ_VIRTUAL_HOST")
    username = os.getenv("SPRING_RABBITMQ_USERNAME")
    password = os.getenv("SPRING_RABBITMQ_PASSWORD")

    def __init__(self):
        self.connection = None
    
    def connect(self):
        logger.info(f"Attempting to connect to RabbitMQ at ${self.host, self.port, self.virtual_host, self.username, self.password, self.CODE_QUEUE_NAME}")
        self.connection =  pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                virtual_host=self.virtual_host,
                credentials=pika.PlainCredentials(
                    username=self.username,
                    password=self.password,
                ),
                heartbeat=600
            )
        )
        # bind to code.block.execute routing key and exchange code-blocks
        channel =  self.connection.channel()
        # make exchange code-blocks
        channel.exchange_declare(self.CODE_BLOCKS_EXCHANGE, exchange_type="topic", durable=True)
        channel.queue_declare(self.CODE_QUEUE_NAME, durable=True)
        logger.info(f"Connected to RabbitMQ at ${self.host, self.port, self.virtual_host, self.username, self.password, self.CODE_QUEUE_NAME}")
        channel.queue_bind(self.CODE_QUEUE_NAME, "code-blocks", "code.block.execute")
        return channel
        