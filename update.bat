@echo off
echo Menunggu proses aplikasi ditutup untuk memulai pembaruan...
timeout /t 2 /nobreak >nul
git stash
git pull origin main
start python main.py
exit
