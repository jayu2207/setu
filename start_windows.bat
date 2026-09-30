@echo off
echo ============================================
echo   Setu - Student-Alumni Platform (Django)
echo ============================================

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt

echo Applying database migrations...
python manage.py migrate

echo Starting server...
python manage.py runserver 0.0.0.0:5000

pause
