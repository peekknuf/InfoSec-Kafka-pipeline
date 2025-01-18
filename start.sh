#!/bin/bash
# Start the producer and consumer in the background
python producer/producer.py &
python consumer/consumer.py &

# Wait for both processes to finish
wait
