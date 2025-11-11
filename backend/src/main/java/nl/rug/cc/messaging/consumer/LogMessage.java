package nl.rug.cc.messaging.consumer;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Getter;
import lombok.Setter;
import nl.rug.cc.messaging.consumer.LogMetadata;
import org.springframework.data.annotation.Id;

import java.io.Serializable;
import java.util.UUID;

@Getter
public class LogMessage implements Serializable {
        @JsonProperty("id")
        @Id
        private UUID id;
        @JsonProperty("content")
        @Setter
        private String content;

        @JsonProperty("metadata")
        @Setter
        private LogMetadata metadata;

        public LogMessage(
                UUID id,
                String content,
                LogMetadata metadata
        ) {
                this.id = id;
                this.content = content;
                this.metadata = metadata;
        }

        public LogMessage(){}
}
