@echo off
echo ==============================================
echo Ogrenci Rehberi Baslatiliyor...
echo ==============================================

echo.
echo Ipuclari: Veritabanini guncellemek (yeni belge eklemek) icin 'veritabani_guncelle.bat' dosyasini calistirin.

echo Adim 2: FastAPI Sunucusu arka planda baslatiliyor...
start /B venv\Scripts\uvicorn.exe src.server:app --port 8000

echo.
echo Adim 3: Modern React Arayuzu baslatiliyor...
start http://localhost:5173/
cd frontend
call npm run dev

pause
