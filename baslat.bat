@echo off
echo ==============================================
echo Mevzuat AI (Akademik Asistan) Baslatiliyor...
echo ==============================================

echo.
echo Adim 1: Mevzuat belgeleri veritabanina kaydediliyor...
call venv\Scripts\python.exe src\ingest.py

echo.
echo Adim 2: FastAPI Sunucusu arka planda baslatiliyor...
start /B venv\Scripts\uvicorn.exe src.server:app --port 8000

echo.
echo Adim 3: Modern React Arayuzu baslatiliyor...
start http://localhost:5173/
cd frontend
call npm run dev

pause
