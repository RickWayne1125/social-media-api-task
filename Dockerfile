# Use an official Python runtime as the base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Redis
RUN apt-get update && apt-get install -y redis-server

## Copy the Redis configuration file
#COPY redis.conf /etc/redis/redis.conf

# Copy the Flask application code into the container
COPY . .

# Expose the port that the Flask application will run on
EXPOSE 5000

# Set the environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Start Redis server
CMD redis-server /etc/redis/redis.conf & \
    flask run --host=0.0.0.0
