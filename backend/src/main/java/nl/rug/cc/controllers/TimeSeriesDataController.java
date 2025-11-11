package nl.rug.cc.controllers;

import nl.rug.cc.dtos.TimeSeriesData;
import nl.rug.cc.dtos.DataAndIp;
import nl.rug.cc.services.TimeSeriesDataService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.http.ResponseEntity;

import java.io.IOException;
import java.text.ParseException;
import java.util.Date;
import java.util.List;

@RestController
@RequestMapping("/timeseries")
public class TimeSeriesDataController {

    @Autowired
    private TimeSeriesDataService service;

    @PostMapping
    public void saveData(@RequestBody TimeSeriesData data) {
        service.saveData(data);
    }

    // Date format 2024-03-15T14:30:00
    @GetMapping
    public List<TimeSeriesData> getData(
        @RequestParam String country,
        @RequestParam(required = false, defaultValue = "") String startDate,
        @RequestParam(required = false, defaultValue = "") String endDate,
        @RequestParam(required = false, defaultValue = "100") Integer limit) {
        DataAndIp dataAndIp = service.getData(country, startDate, endDate, limit); 
        return dataAndIp.getData();
    }

    @PostMapping("/upload")
    public ResponseEntity<String> uploadCsv(@RequestParam("file") MultipartFile file) {
        try {
            service.processCsv(file);
            return ResponseEntity.ok("CSV file processed and data saved to the database.");
        } catch (IOException | ParseException e) {
            return ResponseEntity.badRequest().body("Failed to process CSV file: " + e.getMessage());
        }
    }

    @PostMapping("/delete")
    public ResponseEntity<String> deleteCsv(@RequestParam("dataId") String dataId) {
        /** Id should be unique identifier */
        /** Should check for permissions before deleting */
        if (dataId != null) {
            return ResponseEntity.ok("Data has been deleted");
        }
        return ResponseEntity.badRequest().body("Failed to delete CSV file." );
    }
}