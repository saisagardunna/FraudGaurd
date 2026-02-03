#!/bin/bash

# Start the Telegram Bot in the background
python manage.py run_telegram_bot &

# Start the Web Server in the foreground (so the container stays running)
exec gunicorn credit_card.wsgi:application --bind 0.0.0.0:7860
