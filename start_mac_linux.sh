#!/bin/bash
echo "============================================"
echo "  Setu - Student-Alumni Platform (Django)"
echo "============================================"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Applying database migrations..."
python manage.py migrate

echo "Starting server..."
python manage.py runserver 0.0.0.0:5000
