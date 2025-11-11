#!/bin/bash
# Set connection parameters
CASSANDRA_HOST="cassandra-release.default.svc.cluster.local"
CASSANDRA_PORT=9042
MAX_RETRIES=30
RETRY_DELAY=5

# Wait for Cassandra to be ready
echo "Waiting for Cassandra to become available..."
for ((i=1; i<=$MAX_RETRIES; i++)); do
    if cqlsh --connect-timeout=10 $CASSANDRA_HOST $CASSANDRA_PORT -e "DESCRIBE KEYSPACES" &> /dev/null; then
        echo "Cassandra is available!"
        break
    else
        echo "Attempt $i/$MAX_RETRIES: Cassandra not yet available (retrying in $RETRY_DELAY seconds)..."
        sleep $RETRY_DELAY
    fi
    
    if [ $i -eq $MAX_RETRIES ]; then
        echo "Error: Cassandra not available after $MAX_RETRIES attempts"
        exit 1
    fi
done

# Create keyspace
echo "Creating keyspace..."
cqlsh $CASSANDRA_HOST $CASSANDRA_PORT -e "
CREATE KEYSPACE IF NOT EXISTS mykeyspace 
WITH replication = {
    'class': 'SimpleStrategy', 
    'replication_factor': 1
};"

# Create table
echo "Creating table..."
cqlsh $CASSANDRA_HOST $CASSANDRA_PORT -e "
USE mykeyspace;
CREATE TABLE IF NOT EXISTS timeseries_data (
    country TEXT,
    timestamp TIMESTAMP,
    value DOUBLE,
    resourceId TEXT,
    PRIMARY KEY (country, timestamp)
);"

echo "Initialization completed successfully!"