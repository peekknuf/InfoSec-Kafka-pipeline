from unittest.mock import patch, MagicMock
from src.consumer.consumer import create_kafka_consumer, create_postgres_connection


def test_create_kafka_consumer():
    with patch("confluent_kafka.Consumer") as mock_consumer:
        mock_consumer.return_value = MagicMock()
        consumer = create_kafka_consumer()
        assert consumer is not None


def test_create_postgres_connection():
    with patch("psycopg2.connect") as mock_connect:
        mock_connect.return_value = MagicMock()
        conn = create_postgres_connection()
        assert conn is not None
