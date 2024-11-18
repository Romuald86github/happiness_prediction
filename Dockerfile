# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy the application's requirements file to the container
COPY requirements.txt /app/

# Install application dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code to the container
COPY . /app/

# Expose the application port
EXPOSE 5000

# Command to run the app using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app.app:app"]
