#!/bin/bash
echo "Starting backend with Gunicorn..."
gunicorn --bind 0.0.0.0:$PORT app:app