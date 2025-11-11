package nl.rug.cc.messaging.producer;

import lombok.extern.slf4j.Slf4j;
import nl.rug.cc.config.RabbitConfig;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

@Slf4j
@Component
public class MessageProducer {

    private final RabbitTemplate rabbitTemplate;

    @Autowired
    public MessageProducer(RabbitTemplate rabbitTemplate) {
        this.rabbitTemplate = rabbitTemplate;
    }

    public void send(NewCodeBlockMessage message) {
        log.info("Sending new code block message: {}", message);
        rabbitTemplate.convertAndSend(
                RabbitConfig.CODE_BLOCKS_TOPIC,
                "code.block.execute",
                message
        );
    }

}
