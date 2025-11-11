package nl.rug.cc.config;

import org.springframework.beans.factory.annotation.Value;
import com.datastax.oss.driver.api.core.CqlSession;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import java.net.InetSocketAddress;

@Configuration
public class CassandraConfig {

    @Value("${spring.data.cassandra.host}")
    private String cassandraHost;

    @Value("${spring.data.cassandra.port}")
    private int cassandraPort;

    @Value("${spring.data.cassandra.username}")
    private String username;

    @Value("${spring.data.cassandra.password}")
    private String password;

    @Bean
    public CqlSession cassandraSession() {
        return CqlSession.builder()
                .addContactPoint(new InetSocketAddress(cassandraHost, cassandraPort))
                .withAuthCredentials(username, password)
                .withLocalDatacenter("datacenter1")
                .withKeyspace("mykeyspace")
                .build();
    }
}