package nl.rug.cc.dtos;

import nl.rug.cc.dtos.TimeSeriesData;
import java.util.List;
import lombok.Getter;

@Getter
public class DataAndIp {
    private List<TimeSeriesData> data;
    private String ip;

    public DataAndIp(List<TimeSeriesData> data, String ip) {
        this.data = data;
        this.ip = ip;
    }
}