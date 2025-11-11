package nl.rug.cc.dtos;

import lombok.Data;
import lombok.Getter;
import org.springframework.data.cassandra.core.cql.PrimaryKeyType;
import org.springframework.data.cassandra.core.mapping.PrimaryKeyColumn;
import org.springframework.data.cassandra.core.mapping.PrimaryKeyClass;
import java.io.Serializable;
import java.time.Instant;

@Getter
@Data
@PrimaryKeyClass
public class TimeSeriesKey implements Serializable {

    @PrimaryKeyColumn(name = "country", type = PrimaryKeyType.PARTITIONED)
    private String country;

    @PrimaryKeyColumn(name = "timestamp", type = PrimaryKeyType.CLUSTERED)
    private Instant timestamp;

    public TimeSeriesKey(String country, Instant timestamp) {
        this.country = country;
        this.timestamp = timestamp;
    }
}