
# Use an official Python runtime as a parent image
# Using 3.8 based on TensorFlow 2.4 compatibility
FROM python:3.8-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
# libgl1-mesa-glx is often needed for opencv (cv2)
# gcc and python3-dev are needed for building some python packages
RUN apt-get update && apt-get install -y \
    gcc \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Collect static files
# RUN python manage.py collectstatic --noinput
# (Commented out because it might fail without proper static storage config, enables manual run if needed)

# Expose port 7860 (Hugging Face Default)
EXPOSE 7860

# Default command (overridden by Render/Docker Compose)
# Start both the web server and the telegram bot
CMD gunicorn credit_card.wsgi:application --bind 0.0.0.0:7860 & python manage.py run_telegram_bot
