@echo off
echo Setting up environment...
if not exist venv (
    python -m venv venv
    call .\venv\Scripts\activate
    pip install -r requirements.txt
) else (
    call .\venv\Scripts\activate
)

echo Seeding data...
python seed_data.py

echo Starting Server...
start "FastAPI Server" cmd /k "uvicorn app:app --host 0.0.0.0 --port 8000 --reload"

echo Waiting for server to start...
timeout /t 10 /nobreak

echo Running Tests...
python test_endpoints.py

echo Done.
pause
