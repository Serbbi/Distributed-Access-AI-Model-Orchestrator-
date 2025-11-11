package nl.rug.cc.managers;

import nl.rug.cc.dtos.CodeBlockRequest;
import nl.rug.cc.dtos.CodeBlockResponse;
import nl.rug.cc.messaging.producer.MessageProducer;
import nl.rug.cc.messaging.producer.NewCodeBlockMessage;
import nl.rug.cc.dtos.TimeSeriesData;
import nl.rug.cc.dtos.TimeSeriesKey;
import nl.rug.cc.dtos.DataAndIp;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.util.UUID;
import java.io.IOException;
import java.io.ByteArrayOutputStream;
import java.io.PrintWriter;
import java.util.zip.ZipOutputStream;
import java.util.zip.ZipInputStream;
import java.util.zip.ZipEntry;
import java.io.ByteArrayInputStream;
import java.util.List;
import java.io.FileInputStream;
import java.io.File;

@Component
public class CodeBlockManager {

    private final MessageProducer messageProducer;

    @Autowired
    public CodeBlockManager(MessageProducer messageProducer) {
        this.messageProducer = messageProducer;
    }

    public CodeBlockResponse execNewCodeBlock(File file, DataAndIp dataAndIp) {
        UUID jobId = UUID.randomUUID();
        List<TimeSeriesData> timeSeriesData = dataAndIp.getData();
        String ip = dataAndIp.getIp();
        
        try {
            // 1. Convert time series data to CSV
            byte[] csvData = convertToCsv(timeSeriesData);
            
            // 2. Get original ZIP bytes
            byte[] byteArray = new byte[(int) file.length()];
            try (FileInputStream fis = new FileInputStream(file)) {
                fis.read(byteArray);
            }
            byte[] originalZip = byteArray;
            
            // 3. Create new ZIP with original content + CSV
            byte[] combinedZip = addFileToZip(originalZip, "time_series_data.csv", csvData);
            
            // 4. Create and send message
            NewCodeBlockMessage message = new NewCodeBlockMessage(
                jobId,
                combinedZip,
                ip
            );
            messageProducer.send(message);
            
            return new CodeBlockResponse(jobId, "Processing started successfully");
            
        } catch (IOException e) {
            throw new RuntimeException("Failed to process code block", e);
        }
    }

    private byte[] convertToCsv(List<TimeSeriesData> data) throws IOException {
        try (ByteArrayOutputStream out = new ByteArrayOutputStream();
            PrintWriter writer = new PrintWriter(out)) {
            
            // Write CSV header
            writer.println("Date,Value,Country,ResourceId");
            
            // Write data rows
            for (TimeSeriesData item : data) {
                TimeSeriesKey key = item.getKey();
                writer.printf("%s,%f,%s,%s\n",
                    key.getTimestamp(),
                    item.getValue(),
                    key.getCountry(),
                    item.getResourceId());
            }
            writer.flush();
            return out.toByteArray();
        }
    }

    private byte[] addFileToZip(byte[] originalZip, String filename, byte[] fileContent) throws IOException {
        try (ByteArrayOutputStream baos = new ByteArrayOutputStream();
            ZipOutputStream zos = new ZipOutputStream(baos);
            ZipInputStream zis = new ZipInputStream(new ByteArrayInputStream(originalZip))) {
            
            // 1. Copy all existing entries from original ZIP
            ZipEntry entry;
            while ((entry = zis.getNextEntry()) != null) {
                zos.putNextEntry(new ZipEntry(entry.getName()));
                zis.transferTo(zos);
                zos.closeEntry();
            }
            
            // 2. Add new CSV file
            zos.putNextEntry(new ZipEntry(filename));
            zos.write(fileContent);
            zos.closeEntry();
            
            zos.finish();
            return baos.toByteArray();
        }
    }
}
