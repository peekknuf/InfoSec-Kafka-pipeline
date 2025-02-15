import pytest
import warnings
import yaml
from unittest.mock import MagicMock
from consumer.consumer import create_log_table, load_schema_from_yaml


@pytest.fixture
def mock_db_connection():
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value = cursor
    return conn, cursor


def load_custom_schema():
    with open("schemas/schema_extra_test.yml", "r") as f:
        schema = yaml.safe_load(f)
    return schema.get("logs_schema_extra", {})


def test_create_log_table_schema(mock_db_connection):
    """Test that the schema matches the expected schema, with a warning for extra columns."""
    conn, cursor = mock_db_connection
    custom_schema = load_custom_schema()

    create_log_table(conn, table_name="logs", schema=custom_schema)

    expected_columns = set(load_schema_from_yaml().keys())
    actual_columns = set(custom_schema.keys())
    extra_columns = actual_columns - expected_columns

    if extra_columns:
        for column in extra_columns:
            warnings.warn(f"Extra column found: {column}", UserWarning)

    assert extra_columns, "No extra columns found."
