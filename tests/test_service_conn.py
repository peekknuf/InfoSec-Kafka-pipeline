import unittest
from unittest.mock import patch, MagicMock
from consumer.consumer import create_kafka_consumer, create_postgres_connection

class TestKafkaConsumer(unittest.TestCase):
    @patch("confluent_kafka.Consumer")
    def test_create_kafka_consumer(self, mock_consumer):
        mock_consumer.return_value = MagicMock()
        consumer = create_kafka_consumer()
        self.assertIsNotNone(consumer)

class TestPostgreSQLConnection(unittest.TestCase):
    @patch("psycopg2.connect")
    def test_create_postgres_connection(self, mock_connect):
        mock_connect.return_value = MagicMock()
        conn = create_postgres_connection()
        self.assertIsNotNone(conn)

if __name__ == "__main__":
    unittest.main()
