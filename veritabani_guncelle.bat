@echo off
echo ==============================================
echo Ogrenci Rehberi - Veritabani Guncelleme
echo ==============================================

echo.
echo Belgeler okunuyor ve veritabanina kaydediliyor...
call venv\Scripts\python.exe src\ingest.py

echo.
echo Veritabani guncelleme tamamlandi!
pause
