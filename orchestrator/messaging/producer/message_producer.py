from .log_message import LogMessage

import logging

logger = logging.getLogger(__name__)

class MessageProducer():
    def __init__(self, config):
        self.config = config
        self.channel =  self.config.connect()

    def send_message(self, message: LogMessage):
        self.channel =  self.config.connect()
        logger.info(f"Sending message: {message}")
        self.channel.basic_publish(
            exchange=self.config.LOGS_EXCHANGE,
            routing_key=self.config.LOGS_ROUTING_KEY,
            body=message.json()
        )
        # close the connection
        self.channel.close()
        logger.info(f"Sent message: {message}")

