import os
import logging
import re
from confluent_kafka import Consumer, KafkaError, KafkaException
import psycopg2
from dotenv import load_dotenv

load_dotenv()

KAFKA_TOPIC = os.getenv("KAFKA_TOPIC")
KAFKA_BROKER = os.getenv("KAFKA_BROKER")
GROUP_ID = os.getenv("GROUP_ID")

POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

log_pattern = re.compile(
    r"(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+[+-]\d{2}:\d{2}) \| "
    r"(?P<log_id>ACT-\d{8}T\d{6}-\d+) \| "
    r"(?P<event_type>[A-Z_]+) \| "
    r"user_id=(?P<user_id>[^\s]+) "
    r"username=(?P<username>[^|]*?) "
    r"ip_address=(?P<ip_address>[^\s]+) "
    r"country=(?P<country>[^|]*?) "
    r"region=(?P<region>[^|]*?) "
    r"city=(?P<city>[^|]*?) "
    r"coordinates=(?P<coordinates>[^|]*?) "
    r"os=(?P<os>[^|]*?) "
    r"browser=(?P<browser>[^|]*?) "
    r"device_type=(?P<device_type>[^|]*?) \| "
    r"action=(?P<action>[^|\s]*) "
    r"status=(?P<status>[^|\s]*) \| "
    r"session_id=(?P<session_id>[^|\s]*) "
    r"request_id=(?P<request_id>[^|\s]*) "
    r"trace_id=(?P<trace_id>[^|\s]*)"
)

def create_postgres_connection():
    """Create a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
        )
        logging.info("Connected to PostgreSQL database.")
        return conn
    except Exception as e:
        logging.error(f"Failed to connect to PostgreSQL: {e}")
        raise

def create_log_table(conn):
    """Create the logs table if it doesn't exist."""
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS logs (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    log_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    user_id TEXT,
                    username TEXT,
                    ip_address TEXT,
                    country TEXT,
                    region TEXT,
                    city TEXT,
                    coordinates TEXT,
                    os TEXT,
                    browser TEXT,
                    device_type TEXT,
                    action TEXT,
                    status TEXT,
                    session_id TEXT,
                    request_id TEXT,
                    trace_id TEXT
                );
                """
            )
            conn.commit()
            logging.info("Created logs table (if it didn't exist).")
    except Exception as e:
        logging.error(f"Failed to create logs table: {e}")
        raise

def create_extension(conn):
    try:
        with conn.cursor() as cursor:
            cursor.execute(
             """
             CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
             """
            )
            conn.commit()
            logging.info("Created timescaledb extension (if it didn't exist).")
    except Exception as e:
        logging.error(f"Failed to create timescaledb extension: {e}")
        raise


def create_hypertable(conn):
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT create_hypertable('logs', 'timestamp', chunk_time_interval => INTERVAL '1 second');
                """
            )
            conn.commit()
            logging.info("Created hypertable.")
    except Exception as e:
        logging.error(f"Failed to create hypertable: {e}")
        raise


def insert_log(conn, log_data):
    """Insert a log message into the PostgreSQL database."""
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO logs (
                    timestamp, log_id, event_type, user_id, username, ip_address,
                    country, region, city, coordinates, os, browser, device_type,
                    action, status, session_id, request_id, trace_id
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                );
                """,
                log_data,
            )
            conn.commit()
            logging.info(f"Inserted log into PostgreSQL: {log_data[1]}")
    except Exception as e:
        logging.error(f"Failed to insert log into PostgreSQL: {e}")
        raise

def parse_log(log_message):
    """Parse the log message into its components."""
    match = log_pattern.match(log_message)
    if match:
        # Replace empty strings with None for optional fields
        def replace_empty_with_none(value):
            return value if value else None

        return (
            match.group("timestamp"), 
            match.group("log_id"), 
            match.group("event_type"),
            replace_empty_with_none(match.group("user_id")), 
            replace_empty_with_none(match.group("username")),
            replace_empty_with_none(match.group("ip_address")),
            replace_empty_with_none(match.group("country")),
            replace_empty_with_none(match.group("region")),
            replace_empty_with_none(match.group("city")),
            replace_empty_with_none(match.group("coordinates")),
            replace_empty_with_none(match.group("os")),
            replace_empty_with_none(match.group("browser")),
            replace_empty_with_none(match.group("device_type")),
            replace_empty_with_none(match.group("action")), 
            replace_empty_with_none(match.group("status")),
            replace_empty_with_none(match.group("session_id")),
            replace_empty_with_none(match.group("request_id")),
            replace_empty_with_none(match.group("trace_id")),
        )
    else:
        logging.warning(f"Log format is invalid: {log_message}")
        return None

def create_kafka_consumer():
    """Create and configure a Kafka consumer."""
    try:
        consumer = Consumer(
            {
                "bootstrap.servers": KAFKA_BROKER,
                "group.id": GROUP_ID,
                "auto.offset.reset": "latest",
            }
        )
        consumer.subscribe([KAFKA_TOPIC])
        logging.info(f"Subscribed to Kafka topic: {KAFKA_TOPIC}")
        return consumer
    except Exception as e:
        logging.error(f"Failed to create Kafka consumer: {e}")
        raise

def consume_logs():
    conn = create_postgres_connection()
    create_log_table(conn)
    create_extension(conn)
    create_hypertable(conn)
    consumer = create_kafka_consumer()

    try:
        logging.info("Starting the Kafka consumer loop...")
        while True:
            logging.debug("Polling for messages...")
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                logging.debug("No message received.")
                continue

            if msg.error():
                logging.error(f"Kafka error: {msg.error()}")
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    logging.info(f"End of partition reached: {msg.partition()}")
                else:
                    raise KafkaException(msg.error())
            else:
                log_message = msg.value().decode("utf-8")
                logging.debug(f"Received log message: {log_message}")
                log_data = parse_log(log_message)
                if log_data:
                    insert_log(conn, log_data)
    except KeyboardInterrupt:
        logging.info("Consumer interrupted by user.")
    except Exception as e:
        logging.error(f"Unexpected error in consumer loop: {e}")
        raise
    finally:
        consumer.close()
        conn.close()
        logging.info("Kafka consumer and PostgreSQL connection closed.")

if __name__ == "__main__":
    consume_logs()
