# Use Python 3.11 as the base image
FROM python:3.11-slim-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpango1.0-dev \
    libharfbuzz-dev \
    libfreetype6-dev \
    libfontconfig1-dev \
    libcairo2-dev \
    libpq-dev \
    gcc \
    fontconfig \
    libffi-dev \
    libgdk-pixbuf2.0-0 \
    shared-mime-info \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Copy Times New Roman font
COPY ./fonts/times.ttf /app/fonts/times.ttf

# Copy .env file
#COPY .env /app/.env

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . /app/

# Create necessary directories and set permissions
RUN mkdir -p /app/uploaded_files /app/output && \
    chmod 777 /app/uploaded_files /app/output

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]