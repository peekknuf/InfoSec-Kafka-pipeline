# Base image with Python
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source code into the container
COPY producer/ ./producer/
COPY consumer/ ./consumer/

# Set the default command to use Python
CMD ["python"]

