#!/bin/bash
echo "Starting Crop Disease Detection Backend..."

# Download model if not exists
python download_model.py

# Start the application
python app.py
