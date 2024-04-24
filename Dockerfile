# Use a base image that includes Python and allows for easy installation of other dependencies
FROM ubuntu:latest

# Install necessary tools and libraries
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    libkrb5-dev \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3 as the default Python version
RUN ln -s /usr/bin/python3 /usr/bin/python

# Set the working directory
WORKDIR /usr/src/app

# Copy your application code
COPY . .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable (consider using secrets for sensitive data)
ENV API_KEY "6845365315:AAEjLspSJ7X8wQot7NnE3zO27y20Mxscfqg"

# Command to run the application
CMD ["python3", "main.py"]
