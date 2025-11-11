package nl.rug.cc.controllers;

import jakarta.validation.Valid;
import nl.rug.cc.dtos.CodeBlockRequest;
import nl.rug.cc.dtos.CodeBlockResponse;
import nl.rug.cc.managers.CodeBlockManager;
import nl.rug.cc.services.AuthService;
import nl.rug.cc.services.TimeSeriesDataService;
import nl.rug.cc.dtos.DataAndIp;
import org.springframework.http.HttpHeaders;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.http.ResponseEntity;
import org.springframework.http.HttpStatus;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.bind.annotation.RequestPart;
import org.springframework.http.MediaType;

import java.util.List;
import java.util.Set;
import java.io.File;

@RestController
@RequestMapping("/train")
public class CodeBlockController {

    private final AuthService authService;

    @Autowired
    private TimeSeriesDataService timeSeriesDataService;
    private final CodeBlockManager codeBlockManager;

    @Autowired
    public CodeBlockController(CodeBlockManager codeBlockManager, AuthService authService) {
        this.codeBlockManager = codeBlockManager;
        this.authService = authService;
    }

    @GetMapping(value = "/execute")
    public ResponseEntity<CodeBlockResponse> getNew(
        @RequestHeader(value = HttpHeaders.COOKIE, required = false) String cookieHeader,
        @RequestParam String dataId,
        @RequestParam String modelId) {
        
        File zip = new File("model.zip");
        DataAndIp dataAndIp = timeSeriesDataService.getDataNew(dataId);
        CodeBlockResponse response = codeBlockManager.execNewCodeBlock(zip, dataAndIp);            
        return ResponseEntity.ok(response);
    }
}
