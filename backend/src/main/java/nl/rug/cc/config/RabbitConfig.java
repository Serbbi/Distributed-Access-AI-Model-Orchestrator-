package nl.rug.cc.config;

import org.springframework.amqp.core.Binding;
import org.springframework.amqp.core.BindingBuilder;
import org.springframework.amqp.core.Queue;
import org.springframework.amqp.core.TopicExchange;
import org.springframework.amqp.rabbit.connection.ConnectionFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.amqp.support.converter.Jackson2JsonMessageConverter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class RabbitConfig {
    public static final String CODE_BLOCKS_TOPIC = "code-blocks";

    public static final String LOGS_QUEUE_NAME = "logs-queue-backend";

    public static final String TOPIC_NAME = "logs";

    @Bean
    public RabbitTemplate rabbitTemplate(final ConnectionFactory connectionFactory) {
        final var rabbitTemplate = new RabbitTemplate(connectionFactory);
        rabbitTemplate.setMessageConverter(producerJackson2MessageConverter());
        return rabbitTemplate;
    }

    @Bean
    public Jackson2JsonMessageConverter producerJackson2MessageConverter() {
        return new Jackson2JsonMessageConverter();
    }

    // create topic exchange
    @Bean
    TopicExchange exchange() {
        return new TopicExchange(TOPIC_NAME);
    }

    @Bean
    Queue logsQueue() {
        return new Queue(LOGS_QUEUE_NAME, true);
    }

    @Bean
    Binding secondBinding(Queue logsQueue, TopicExchange exchange) {
        return BindingBuilder
                .bind(logsQueue)
                .to(exchange)
                .with("logs.job.*");
    }
}
