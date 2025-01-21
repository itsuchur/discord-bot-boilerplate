# Dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better cache utilization
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

COPY entrypoint.sh .
RUN chmod 755 entrypoint.sh

# Run the bot
ENTRYPOINT ["/bin/bash", "./entrypoint.sh"]