#!/bin/bash
echo "Setting up backend..."
cd backend/model
python download_model.py
cd ..
python app.py
