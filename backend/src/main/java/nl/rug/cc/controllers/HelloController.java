package nl.rug.cc.controllers;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;


import java.util.Date;
import java.util.UUID;


@RestController
public class HelloController {

    @Autowired
    private RabbitTemplate rabbitTemplate;

    @GetMapping("/hello")
    public ResponseEntity<String> healthCheck() {
        StringBuilder healthStatus = new StringBuilder("Hello world! " + new Date() + "\n");

        // RabbitMQ Health Check
        try {
            rabbitTemplate.execute(channel -> {
                channel.basicQos(1);  // Dummy operation to ensure the connection is valid
                return true;
            });
            healthStatus.append("RabbitMQ: Connected\n");
        } catch (Exception e) {
            healthStatus.append("RabbitMQ: Connection Failed - ").append(e.getMessage()).append("\n");
            return new ResponseEntity<String>(healthStatus.toString() + "Service connection failed: " + e.getMessage(), HttpStatus.HTTP_VERSION_NOT_SUPPORTED);
        }

        return new ResponseEntity<String>(healthStatus.toString(), HttpStatus.OK);
    }
}
