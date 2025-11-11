package nl.rug.cc.dtos;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.bind.annotation.RequestPart;

import java.util.List;


public record CodeBlockRequest(
        @RequestPart("codeZipFile") MultipartFile codeZipFile
) {}
