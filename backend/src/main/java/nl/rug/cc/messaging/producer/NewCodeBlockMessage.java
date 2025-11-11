package nl.rug.cc.messaging.producer;

import lombok.Getter;
import lombok.Setter;
import java.io.Serializable;
import java.util.UUID;
import java.util.List;

import com.fasterxml.jackson.annotation.JsonProperty;

@Getter
@Setter
public class NewCodeBlockMessage implements Serializable {
    private UUID id;
    private byte[] code;
    private String cassandra_pod_ip;
    
    public NewCodeBlockMessage(UUID id, byte[] zipFile, String cassandra_pod_ip) {
        this.id = id;
        this.code = zipFile;
        this.cassandra_pod_ip = cassandra_pod_ip;
    }
}
