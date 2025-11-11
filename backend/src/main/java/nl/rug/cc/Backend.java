package nl.rug.cc;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cache.annotation.EnableCaching;

@SpringBootApplication
@EnableCaching
public class Backend {
    public static void main(String[] args) {
        SpringApplication
                .run(Backend.class, args);
    }
}
