# Use Python 3.11 as base image (you can change to 3.9 if you want)
FROM python:3.11-slim

# -------------------------------
# Set working directory
WORKDIR /app

# -------------------------------
# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# -------------------------------
# Copy requirements file
COPY requirements.txt .

# -------------------------------
# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# -------------------------------
# Create necessary directories (customize as needed)
RUN mkdir -p /app/input \
    /app/output1 \
    /app/generated_notes \
    && chmod -R 777 /app/input /app/output1 /app/generated_notes

# -------------------------------
# Copy the application code
COPY . /app/

# -------------------------------
# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# -------------------------------
# Expose the port the app runs on
EXPOSE 8000

# -------------------------------
# Command to run the FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]