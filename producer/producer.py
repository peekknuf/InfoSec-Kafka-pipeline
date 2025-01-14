import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from confluent_kafka import Producer

LOG_FILE_PATH = "/app/logs/logs.log"  # Path to the log file in the mounted volume
KAFKA_TOPIC = "log_topic"
KAFKA_BROKER = "kafka:9092"

# Kafka producer configuration
producer = Producer({"bootstrap.servers": KAFKA_BROKER})


class LogHandler(FileSystemEventHandler):
    """Handles changes to the log file."""

    def on_modified(self, event):
        if event.src_path == LOG_FILE_PATH:
            with open(LOG_FILE_PATH, "r") as f:
                lines = f.readlines()
                last_line = lines[-1].strip()
                if last_line:  # Check if the line is not empty
                    producer.produce(KAFKA_TOPIC, value=last_line)
                    producer.flush()


if __name__ == "__main__":
    event_handler = LogHandler()
    observer = Observer()
    observer.schedule(event_handler, path="/app/logs", recursive=False)
    observer.start()

    print(f"Monitoring {LOG_FILE_PATH} for changes...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

