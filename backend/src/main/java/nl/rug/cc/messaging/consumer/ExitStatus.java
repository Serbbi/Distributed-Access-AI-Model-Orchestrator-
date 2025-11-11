package nl.rug.cc.messaging.consumer;

import lombok.Getter;

@Getter
public enum ExitStatus {
    SUCCESS("SUCCESS"),
    FAILURE("FAILURE"),
    RUNNING("RUNNING"),
    PENDING("PENDING"),
    TIMEOUT("TIMEOUT");

    private String value;

    ExitStatus(String value) {
        this.value = value;
    }

    ExitStatus(){}
}
