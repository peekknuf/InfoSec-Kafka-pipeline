# Log Streaming and Monitoring Pipeline

This project implements a log streaming and monitoring pipeline with real-time visualization. Logs are generated outside the Docker container, processed through Kafka, stored in PostgreSQL, and visualized using Superset and Grafana.

## Architecture Overview

### View the Architecture Diagram:
https://rawcdn.githack.com/peekknuf/streaming_pipeline/refs/heads/main/index.html

### Key Components:
1. **Log Generation**:
   - Logs are generated outside the Docker container with a custom tool and saved in a .log format.
   
2. **Object Storage**:
   - Logs are stored temporarily in a shared object storage location.

3. **Kafka**:
   - **Kafka Producer** reads logs from object storage and streams them into Kafka topics.
   - **Kafka Consumer** processes the log streams and prepares them for storage.

4. **PostgreSQL(TimescaleDB)**:
   - Kafka Consumer writes parsed, processed logs into a PostgreSQL database with TimescaleDB extension.

5. **Visualization**:
   - **Superset** is used to create dashboards for insights from the log data.
   - **Grafana** monitors the pipeline's performance and health.

---

## Prerequisites
### Everything required is in Docker Compose.
- Docker
- Python 3.9+
- Apache Kafka
- PostgreSQL
- Superset
- Grafana

---

Note: this is not a final version, rather a working prototype, work in progress including processing and vizualization tools.

