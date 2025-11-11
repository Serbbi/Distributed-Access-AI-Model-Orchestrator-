package nl.rug.cc.dtos;

import lombok.Data;
import lombok.Getter;
import nl.rug.cc.dtos.TimeSeriesKey;
import org.springframework.data.cassandra.core.mapping.PrimaryKey;
import org.springframework.data.cassandra.core.mapping.Table;

@Getter
@Data
@Table("timeseries_data")
public class TimeSeriesData {

    @PrimaryKey
    private TimeSeriesKey key;

    private double value;

    private String resourceId;

    public TimeSeriesData(TimeSeriesKey key, double value, String resourceId) {
        this.key = key;
        this.value = value;
        this.resourceId = resourceId;
    }
}