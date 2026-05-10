#!/bin/bash
echo "Menunggu aplikasi ditutup untuk memulai pembaruan..."
sleep 2
git stash
git pull origin main
python3 main.py
