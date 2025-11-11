package nl.rug.cc.messaging.consumer;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Getter;
import lombok.Setter;
import org.springframework.data.annotation.Id;

import java.io.Serializable;
import java.util.UUID;

@Getter
@Setter
public class LogMetadata implements Serializable{
    @Id
    @JsonProperty("id")
    private UUID id;

    @JsonProperty("code")
    private String code;

    @JsonProperty("start")
    private Long start;

    @JsonProperty("end")
    private Long end;

    @JsonProperty("duration")
    private Long duration;

    @JsonProperty("status")
    private ExitStatus status;

    @JsonProperty("exitCode")
    private Integer exitCode;

    public LogMetadata(
            UUID id
    ) {
        this.id = id;
    }

    public LogMetadata(){}
}
