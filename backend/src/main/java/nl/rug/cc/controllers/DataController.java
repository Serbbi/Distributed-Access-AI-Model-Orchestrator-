package nl.rug.cc.controllers;

import nl.rug.cc.services.TimeSeriesDataService;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RestController;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.List;
import java.util.Map;
import java.util.Set;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpHeaders;
import nl.rug.cc.services.AuthService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

@RestController
public class DataController {
    @Autowired
    private final AuthService authService;
    @Autowired
    private final TimeSeriesDataService timeSeriesDataService;

    private static final Logger log = LoggerFactory.getLogger(DataController.class);

    @Autowired
    public DataController(AuthService authService, TimeSeriesDataService timeSeriesDataService) {
        this.authService = authService;
        this.timeSeriesDataService = timeSeriesDataService;
    }

    @GetMapping("/models")
    public ResponseEntity<List<Map<String, String>>> getModels(
            @RequestHeader(value = HttpHeaders.COOKIE, required = false) String cookieHeader) {
        log.info("MODELS FETCHING...");
        try {
            if (authService.userHasValidSession(cookieHeader).hasPermission) {
                {
                    String model = "models";
                    String[] modelIds = timeSeriesDataService.getIds("model");
                    log.info("TRYING TO FETCH RESOURCES BY TYPE"); 
                    Set<String> modelList = authService.getUserAccessibleResources(cookieHeader, modelIds);
                    log.info("RESOURCE TYPE COMPLETE");
                    if (modelList.isEmpty()) {
                        log.info("No models found for the user.");
                        return ResponseEntity.ok(List.of());
                    }
                    // Fetch metadata from the database
                    List<Map<String, String>> modelMetadata = timeSeriesDataService.getMetadata(modelList);
                    return new ResponseEntity<List<Map<String, String>>>(modelMetadata, HttpStatus.OK);
                }
            }
            return ResponseEntity.ok(List.of());
        } catch (Exception e) {
            log.info("An error occurred", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(List.of());
        }
    }

    @GetMapping("/data")
    public ResponseEntity<List<Map<String, String>>> getData(
            @RequestHeader(value = HttpHeaders.COOKIE, required = false) String cookieHeader) {
        log.info("DATA FETCHING...");
        try {
            if (authService.userHasValidSession(cookieHeader).hasPermission) {  
                String data = "data";       
                String[] dataIds = timeSeriesDataService.getIds(data);
                Set<String> dataList = authService.getUserAccessibleResources(cookieHeader, dataIds);
                if (dataList.isEmpty()) {
                    log.info("No data found for the user.");
                    return ResponseEntity.ok(List.of());
                }
                log.info("RESOURCE TYPE COMPLETE");
                List<Map<String, String>> dataMetadata = timeSeriesDataService.getMetadata(dataList);
                return new ResponseEntity<List<Map<String, String>>>(dataMetadata, HttpStatus.OK);
            }                
            return ResponseEntity.ok(List.of());
        } catch (Exception e) {
            log.info("An error occurred", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(List.of());
        }
    }
}
