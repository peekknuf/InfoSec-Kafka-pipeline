# Base image with Python
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source code into the container
COPY src/producer/ ./producer/
COPY src/consumer/ ./consumer/
COPY .env .
COPY start.sh .
RUN chmod +x start.sh

# Set the default command to use Python
CMD ["./start.sh"]

