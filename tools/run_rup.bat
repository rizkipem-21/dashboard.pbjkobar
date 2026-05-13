@echo off  
setlocal enabledelayedexpansion
cd /d D:\rup-2026-inaproc

echo ========================= >> tools\log.txt
echo START %date% %time% >> tools\log.txt

:: 1. PROSES DATA (Otomatis Download, JSON, Excel, dan Update Tanggal)
echo RUN GENERATE RUP MULTI-TAHUN >> tools\log.txt
python scripts\rup\generate_rup.py >> tools\log.txt 2>&1

:: 2. PROSES UPLOAD KE GITHUB
echo GIT CONFIG >> tools\log.txt
git config user.name "rizkipem-21"
git config user.email "rizki.pem@gmail.com"

echo GIT STATUS >> tools\log.txt
git status >> tools\log.txt 2>&1

:: FIX LOCK (Mencegah error Git nyangkut)
del /f /q .git\index.lock >nul 2>&1

echo GIT ADD >> tools\log.txt
git add . >> tools\log.txt 2>&1

echo GIT COMMIT >> tools\log.txt
git commit -m "Auto update RUP %date% %time%" >> tools\log.txt 2>&1

echo GIT PUSH >> tools\log.txt
git push origin main >> tools\log.txt 2>&1

echo PUSH STATUS: %ERRORLEVEL% >> tools\log.txt

echo ========================= >> tools\log.txt
echo SELESAI %date% %time% >> tools\log.txt

:: 3. NOTIFIKASI SELESAI (POP-UP ALWAYS ON TOP SELAMA 5 DETIK)
mshta vbscript:Execute("CreateObject(""WScript.Shell"").Popup(""Proses update RUP Multi-Tahun telah SELESAI!"", 5, ""Update Selesai"", 4160)(window.close)")