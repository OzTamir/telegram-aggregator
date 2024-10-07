# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install uv
RUN pip install uv

# Install any needed packages specified in requirements.txt using uv
RUN uv pip install -r requirements.txt

# Define environment variable
ENV NAME TelegramAggregator

# Run main.py when the container launches
CMD ["python", "main.py"]
