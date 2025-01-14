import os
import logging
import re
from confluent_kafka import Consumer, KafkaError, KafkaException
import psycopg2

# Configuration
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "log_topic")
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
GROUP_ID = "log_consumer_group"

# PostgreSQL configuration
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "logs_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


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
                    ip_address TEXT NOT NULL,
                    user_agent TEXT NOT NULL,
                    message TEXT NOT NULL
                );
                """
            )
            conn.commit()
            logging.info("Created logs table (if it didn't exist).")
    except Exception as e:
        logging.error(f"Failed to create logs table: {e}")
        raise


def insert_log(conn, timestamp, ip_address, user_agent, message):
    """Insert a log message into the PostgreSQL database."""
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO logs (timestamp, ip_address, user_agent, message)
                VALUES (%s, %s, %s, %s);
                """,
                (timestamp, ip_address, user_agent, message),
            )
            conn.commit()
            logging.info(f"Inserted log into PostgreSQL: {message}")
    except Exception as e:
        logging.error(f"Failed to insert log into PostgreSQL: {e}")
        raise


def parse_log(log_message):
    """Parse the log message into its components."""
    log_pattern = re.compile(
        r"\[(?P<timestamp>.+)\] IP: (?P<ip_address>.+), UserAgent: (?P<user_agent>.+), Message: (?P<message>.+)"
    )
    match = log_pattern.match(log_message)
    if match:
        return (
            match.group("timestamp"),  # Timestamp
            match.group("ip_address"),  # IP Address
            match.group("user_agent"),  # User Agent
            match.group("message"),  # Message
        )
    else:
        logging.warning(f"Log format is invalid: {log_message}")
        return None


def is_valid_log(log_message):
    """Check if a log message is valid."""
    log_pattern = re.compile(
        r"\[(?P<timestamp>.+)\] IP: (?P<ip_address>.+), UserAgent: (?P<user_agent>.+), Message: (?P<message>.+)"
    )
    return log_pattern.match(log_message) is not None


def create_kafka_consumer():
    """Create and configure a Kafka consumer."""
    try:
        consumer = Consumer(
            {
                "bootstrap.servers": KAFKA_BROKER,
                "group.id": GROUP_ID,
                "auto.offset.reset": "earliest",  # Start reading from the beginning of the topic
            }
        )
        consumer.subscribe([KAFKA_TOPIC])
        logging.info(f"Subscribed to Kafka topic: {KAFKA_TOPIC}")
        return consumer
    except Exception as e:
        logging.error(f"Failed to create Kafka consumer: {e}")
        raise


def consume_logs():
    """Consume logs from Kafka and store them in PostgreSQL."""
    conn = create_postgres_connection()
    create_log_table(conn)
    consumer = create_kafka_consumer()

    try:
        while True:
            msg = consumer.poll(timeout=1.0)  # Poll for new messages
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    logging.info(f"Reached end of partition: {msg.partition()}")
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                log_message = msg.value().decode("utf-8")
                if is_valid_log(log_message):
                    timestamp, ip_address, user_agent, message = parse_log(log_message)
                    insert_log(conn, timestamp, ip_address, user_agent, message)
    except KeyboardInterrupt:
        logging.info("Consumer interrupted by user.")
    finally:
        consumer.close()
        conn.close()
        logging.info("Kafka consumer and PostgreSQL connection closed.")


if __name__ == "__main__":
    consume_logs()
