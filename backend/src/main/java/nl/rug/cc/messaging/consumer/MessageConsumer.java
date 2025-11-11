package nl.rug.cc.messaging.consumer;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.amqp.core.Message;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.amqp.rabbit.listener.api.ChannelAwareMessageListener;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import com.rabbitmq.client.Channel;

import lombok.extern.slf4j.Slf4j;
import nl.rug.cc.config.RabbitConfig;

@Component
@Slf4j
public class MessageConsumer implements ChannelAwareMessageListener {
    private final SimpMessagingTemplate messagingTemplate;
    private final ObjectMapper objectMapper;

    @Autowired
    public MessageConsumer(ObjectMapper objectMapper, SimpMessagingTemplate messagingTemplate) {
        this.objectMapper = objectMapper;
        this.messagingTemplate = messagingTemplate;
    }

    @RabbitListener(
            queues = RabbitConfig.LOGS_QUEUE_NAME,
            ackMode = "MANUAL"
    )
    @Override
    public void onMessage(Message messagePlain, Channel channel) throws Exception {
        try {
            LogMessage message = objectMapper.readValue(messagePlain.getBody(), LogMessage.class);
            log.info("Received new message {}", messagePlain);
            messagingTemplate.convertAndSend("/topic/logs", message);
            channel.basicAck(messagePlain.getMessageProperties().getDeliveryTag(), false);
        } catch (Exception e) {
            log.error("Error processing message: {}", e.getMessage());
            // channel.basicReject(message.getMessageProperties().getDeliveryTag(), false);
        }
    }
}
