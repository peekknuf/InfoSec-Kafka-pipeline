import time
import os
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from confluent_kafka import Producer

# Configuration
LOG_FILE_PATH = "/app/logs/logs.log"  # Path to the log file in the mounted volume
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "log_topic")
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")

# Kafka producer configuration
producer = Producer({"bootstrap.servers": KAFKA_BROKER})

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def send_to_kafka(line):
    """Send a log line to Kafka."""
    try:
        producer.produce(KAFKA_TOPIC, value=line)
        logging.info(f"Sent to Kafka: {line}")
    except Exception as e:
        logging.error(f"Failed to send message to Kafka: {e}")


def read_existing_logs():
    """Read all existing logs from the file and send them to Kafka."""
    if not os.path.exists(LOG_FILE_PATH):
        logging.warning(f"Log file {LOG_FILE_PATH} does not exist.")
        return

    with open(LOG_FILE_PATH, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                send_to_kafka(line)
        producer.flush()  # Ensure all messages are sent


class LogHandler(FileSystemEventHandler):
    """Handles changes to the log file."""

    def __init__(self):
        self.last_position = self.get_file_size()

    def get_file_size(self):
        """Get the current size of the log file."""
        return os.path.getsize(LOG_FILE_PATH)

    def on_modified(self, event):
        if event.src_path == LOG_FILE_PATH:
            with open(LOG_FILE_PATH, "r") as f:
                f.seek(self.last_position)
                new_lines = f.readlines()
                self.last_position = f.tell()

                for line in new_lines:
                    line = line.strip()
                    if line:
                        send_to_kafka(line)
                producer.flush()  # Ensure all messages are sent


if __name__ == "__main__":
    # Read all existing logs at startup
    read_existing_logs()

    # Start monitoring the file for new logs
    event_handler = LogHandler()
    observer = Observer()
    observer.schedule(event_handler, path="/app/logs", recursive=False)
    observer.start()

    logging.info(f"Monitoring {LOG_FILE_PATH} for changes...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
