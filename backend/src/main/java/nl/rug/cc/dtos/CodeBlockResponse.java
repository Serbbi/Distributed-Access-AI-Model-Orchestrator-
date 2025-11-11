package nl.rug.cc.dtos;

import java.util.UUID;

public record CodeBlockResponse(
        UUID jobId,
        String logs) {

}
