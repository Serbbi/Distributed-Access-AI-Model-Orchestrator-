package nl.rug.cc.repositories;

import nl.rug.cc.dtos.TimeSeriesData;
import nl.rug.cc.dtos.TimeSeriesKey;
import org.springframework.data.cassandra.repository.CassandraRepository;
import org.springframework.data.cassandra.repository.Query;
import java.util.Date;
import java.time.Instant;
import java.util.List;

public interface TimeSeriesDataRepository extends CassandraRepository<TimeSeriesData, TimeSeriesKey> {

    @Query("SELECT * FROM timeseries_data WHERE country = ?0 LIMIT ?1")
    List<TimeSeriesData> findByKeyCountry(String country, int limit);
    
    @Query("SELECT * FROM timeseries_data WHERE country = ?0 AND timestamp >= ?1 AND timestamp <= ?2 LIMIT ?3")
    List<TimeSeriesData> findByCountryAndTimestampBetween(
        String country, 
        Instant startDate, 
        Instant endDate, 
        int limit
    );
}