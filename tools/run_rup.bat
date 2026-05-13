@echo off  
setlocal enabledelayedexpansion
cd /d D:\rup-2026-inaproc

echo ========================= >> tools\log_rup.txt
echo START %date% %time% >> tools\log_rup.txt

:: 1. PROSES DATA (Otomatis Download, JSON, Excel, dan Update Tanggal)
echo RUN GENERATE RUP MULTI-TAHUN >> tools\log_rup.txt
python scripts\rup\generate_rup.py >> tools\log_rup.txt 2>&1

:: 2. PROSES UPLOAD KE GITHUB
echo GIT CONFIG >> tools\log_rup.txt
git config user.name "rizkipem-21"
git config user.email "rizki.pem@gmail.com"

echo GIT STATUS >> tools\log_rup.txt
git status >> tools\log_rup.txt 2>&1

:: FIX LOCK (Mencegah error Git nyangkut)
del /f /q .git\index.lock >nul 2>&1

echo GIT ADD >> tools\log_rup.txt
git add . >> tools\log_rup.txt 2>&1

echo GIT COMMIT >> tools\log_rup.txt
git commit -m "Auto update RUP %date% %time%" >> tools\log_rup.txt 2>&1

echo GIT PUSH >> tools\log_rup.txt
git push origin main >> tools\log_rup.txt 2>&1

echo PUSH STATUS: %ERRORLEVEL% >> tools\log_rup.txt

echo ========================= >> tools\log_rup.txt
echo SELESAI %date% %time% >> tools\log_rup.txt

:: 3. NOTIFIKASI SELESAI (POP-UP ALWAYS ON TOP SELAMA 5 DETIK)
mshta vbscript:Execute("CreateObject(""WScript.Shell"").Popup(""Proses update RUP Multi-Tahun telah SELESAI!"", 5, ""Update Selesai"", 4160)(window.close)")