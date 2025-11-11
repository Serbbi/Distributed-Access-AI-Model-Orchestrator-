package nl.rug.cc.services;

import nl.rug.cc.dtos.TimeSeriesData;
import nl.rug.cc.dtos.TimeSeriesKey;
import nl.rug.cc.dtos.DataAndIp;
import nl.rug.cc.repositories.TimeSeriesDataRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;
import org.springframework.web.multipart.MultipartFile;
import com.datastax.oss.driver.api.core.CqlSession;
import com.datastax.oss.driver.api.core.cql.ResultSet;
import com.datastax.oss.driver.api.core.cql.SimpleStatement;
import com.datastax.oss.driver.api.core.cql.Row;
import com.datastax.oss.driver.api.core.cql.Statement;
import com.datastax.oss.driver.api.core.cql.QueryTrace;
import com.datastax.oss.driver.api.core.cql.ExecutionInfo;
import com.datastax.oss.driver.api.core.cql.TraceEvent;

import java.io.IOException;
import java.io.Reader;
import java.io.InputStreamReader;
import java.text.ParseException;
import java.time.format.DateTimeParseException;
import java.util.List;
import java.util.ArrayList;
import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneId;
import java.util.Map;
import java.util.HashMap;
import java.util.Set;

@Service
public class TimeSeriesDataService {

    @Autowired
    private TimeSeriesDataRepository repository;

    @Autowired
    private CqlSession cqlSession;

    public void saveData(TimeSeriesData data) {
        repository.save(data);
    }

    private void printTraceDetails(ResultSet resultSet) {
        ExecutionInfo executionInfo = resultSet.getExecutionInfo();

        try {
            Thread.sleep(10000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        QueryTrace trace = executionInfo.getQueryTrace();

        if (trace != null) {
            System.out.println("Query Trace:");
            for (TraceEvent event : trace.getEvents()) {
                System.out.printf("  %d - %s - %s%n", event.getSourceElapsedMicros(), event.getSource(), event.getActivity());
            }
        } else {
            System.out.println("No trace information available.");
        }
    }

    private String extractCassandraPodIp(ResultSet resultSet) {
        ExecutionInfo executionInfo = resultSet.getExecutionInfo();
        QueryTrace trace = executionInfo.getQueryTrace();

        String cassandraPodIp = null;

        if (trace != null) {
            for (TraceEvent event : trace.getEvents()) {
                if (event.getActivity().contains("Sending RANGE_RSP")) {
                    String[] parts = event.getActivity().split("/");
                    String[] ipParts = parts[1].split(":");
                    cassandraPodIp = ipParts[0];
                    break;
                }
            }
        } 

        return cassandraPodIp;
    }

    public DataAndIp getDataNew(String resourceId) {
        List<TimeSeriesData> timeSeriesDataList = new ArrayList<>();
        String cassandraPodIp = null;

        Statement statement = SimpleStatement.newInstance(
            "SELECT * FROM timeseries_data WHERE resourceId = ? ALLOW FILTERING",
            resourceId
        ).setTracing(true);

        ResultSet resultSet = cqlSession.execute(statement);
        
        printTraceDetails(resultSet);
        cassandraPodIp = extractCassandraPodIp(resultSet);
        System.out.println("Cassandra Pod IP: " + cassandraPodIp);
        resultSet.forEach(row -> {
            TimeSeriesData data = new TimeSeriesData(
                new TimeSeriesKey(row.getString("country"), row.getInstant("timestamp")),
                row.getDouble("value"),
                row.getString("resourceId")
            );
            timeSeriesDataList.add(data);
        });
        return new DataAndIp(timeSeriesDataList, cassandraPodIp);
    }

    public DataAndIp getData(String country, String startDate, String endDate, Integer limit) {
        List<TimeSeriesData> timeSeriesDataList = new ArrayList<>();       
        Instant startInstant = null;
        Instant endInstant = null;
        Statement statement = null; 
        // Validate required parameters
        if (country == null || country.isEmpty()) {
            throw new IllegalArgumentException("Country parameter is required");
        }

        int effectiveLimit = (limit != null && limit > 0) ? limit : 100;

        if (startDate == null || startDate.isEmpty() || endDate == null || endDate.isEmpty()) {
            statement = SimpleStatement.newInstance(
                "SELECT * FROM timeseries_data WHERE country = ? LIMIT ?",
                country,
                limit
            ).setTracing(true);
        } else {
            try {
                // Parse input dates (yyyy-MM-dd) and convert to Instant
                LocalDate startLocalDate = LocalDate.parse(startDate);
                LocalDate endLocalDate = LocalDate.parse(endDate);
                
                startInstant = startLocalDate.atStartOfDay(ZoneId.systemDefault()).toInstant();
                endInstant = endLocalDate.atStartOfDay(ZoneId.systemDefault()).toInstant();
            } catch (DateTimeParseException e) {
                throw new IllegalArgumentException("Invalid date format. Expected yyyy-MM-dd", e);
            }

            statement = SimpleStatement.newInstance(
                "SELECT * FROM timeseries_data WHERE country = ? AND timestamp >= ? AND timestamp <= ? LIMIT ?",
                country,
                startInstant,
                endInstant,
                limit
            ).setTracing(true);
        }

        ResultSet resultSet = cqlSession.execute(statement);

        // Print trace details for debugging
        printTraceDetails(resultSet);
        String cassandraPodIp = extractCassandraPodIp(resultSet);
        System.out.println("Cassandra Pod IP: " + cassandraPodIp);
        
        resultSet.forEach(row -> {
            TimeSeriesData data = new TimeSeriesData(
                new TimeSeriesKey(row.getString("country"), row.getInstant("timestamp")),
                row.getDouble("value"),
                "resourceID"
            );
            timeSeriesDataList.add(data);
        });
        
        return new DataAndIp(timeSeriesDataList, cassandraPodIp);
    }

    public void processCsv(MultipartFile file) throws IOException, ParseException {
        List<TimeSeriesData> dataList = new ArrayList<>();

        try (Reader reader = new InputStreamReader(file.getInputStream());
             CSVParser csvParser = new CSVParser(reader, CSVFormat.DEFAULT.withFirstRecordAsHeader())) {

            for (CSVRecord record : csvParser) {
                String country = record.get("Country");
                String timestampStr = record.get("Date");
                String valueStr = record.get("Value");
                double value = Double.parseDouble(valueStr != "" ? valueStr : "0");

                Instant timestamp = LocalDate.parse(timestampStr)
                .atStartOfDay(ZoneId.systemDefault())
                .toInstant();

                TimeSeriesKey key = new TimeSeriesKey(country, timestamp);
                TimeSeriesData data = new TimeSeriesData(key, value, "resourceID");

                dataList.add(data);
            }
        }

        repository.saveAll(dataList);
    }

        public List<Map<String, String>> getMetadata(Set<String> resourceIDs) throws Exception {
        List<Map<String, String>> metadataList = new ArrayList<>();

        // Fetch all the resourceIDs from the database
        Statement statement = SimpleStatement.newInstance(
            "SELECT * FROM metadata WHERE id IN ? ALLOW FILTERING",
            resourceIDs
        );
        // For every metadata fetched, create a map and add it to the list
        ResultSet resultSet = cqlSession.execute(statement);
        for (Row row : resultSet) {
            Map<String, String> metadata = new HashMap<>();
            metadata.put("title", row.getString("title"));
            metadata.put("type", row.getString("type"));
            metadata.put("description", row.getString("description"));
            metadata.put("id", row.getString("id"));
            metadataList.add(metadata);
        }

        return metadataList;
    }

    public String[] getIds(String type) {
        String[] ids = null;
        Statement statement = SimpleStatement.newInstance(
            "SELECT id FROM metadata WHERE type = ? ALLOW FILTERING",
            type
        );
        ResultSet resultSet = cqlSession.execute(statement);
        List<String> idList = new ArrayList<>();
        for (Row row : resultSet) {
            idList.add(row.getString("id"));
        }
        ids = idList.toArray(new String[0]);
        return ids;
    }
}