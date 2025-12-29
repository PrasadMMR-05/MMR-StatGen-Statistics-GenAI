# PowerShell script to run the MMR Statistics Microservice

$ErrorActionPreference = "Stop"

Write-Host "Checking environment..." -ForegroundColor Cyan

# Check if venv exists, create if not
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
    
    Write-Host "Installing dependencies..."
    .\venv\Scripts\python.exe -m pip install -r requirements.txt
}
else {
    Write-Host "Virtual environment found."
}

# Run Ingestion (using the fixed ingest.py)
Write-Host "Running data ingestion..." -ForegroundColor Cyan
.\venv\Scripts\python.exe ingest.py

# Start Server
Write-Host "Starting FastAPI Server..." -ForegroundColor Cyan
# Start in a new window so it keeps running
Start-Process -FilePath "cmd" -ArgumentList "/k .\venv\Scripts\uvicorn.exe app:app --host 0.0.0.0 --port 8000 --reload"

Write-Host "Waiting 10 seconds for server to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Run Tests
Write-Host "Running API endpoint tests..." -ForegroundColor Cyan
.\venv\Scripts\python.exe test_endpoints.py

Write-Host "Done. The server is still running in the other window." -ForegroundColor Green
# Removed ReadKey for automated execution

