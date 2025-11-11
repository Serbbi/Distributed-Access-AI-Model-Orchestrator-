from ..rabbit_config import RabbitConfig
from .new_code_block_message import NewCodeBlockMessage

import logging
import pika
import time

logger = logging.getLogger(__name__)

class MessageConsumer:
    def __init__(self, config, message_service):
        self.message_service = message_service
        self.config = config
        self.channel = self.config.connect()

    def handle_message(self, ch, method, properties, body: NewCodeBlockMessage):
        logger.info("Received message")
        try:
            body = NewCodeBlockMessage.parse_raw(body)
        except Exception as e:
            logger.error(f"Invalid message received: {e}")
            return
            
        try:
            self.message_service.handle(body, ch, method.delivery_tag)
        except Exception as e:
            logger.error(f"Error while handling message: {e}")

    def start_consuming(self):
        logger.info("Starting to consume messages")
        self.channel.basic_consume(self.config.CODE_QUEUE_NAME, self.handle_message)
        # only handle one message at a time
        self.channel.basic_qos(prefetch_count=1)
        self.channel.start_consuming()
