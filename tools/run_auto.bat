@echo off  
setlocal enabledelayedexpansion
cd /d D:\rup-2026-inaproc

echo ========================= >> tools\log.txt
echo START %date% %time% >> tools\log.txt

echo DOWNLOAD DATA >> tools\log.txt
powershell -ExecutionPolicy Bypass -File tools\download.ps1 >> tools\log.txt 2>&1

echo GENERATE REKAP >> tools\log.txt
python scripts\generate_rup.py >> tools\log.txt 2>&1

echo GENERATE EXCEL >> tools\log.txt
python scripts\generate_excel.py >> tools\log.txt 2>&1

:: FORMAT TANGGAL
for /f "tokens=1-3 delims=/ " %%a in ("%date%") do (
    set dd=%%a
    set mm=%%b
    set yyyy=%%c
)

set bulan=
if "%mm%"=="01" set bulan=Januari
if "%mm%"=="02" set bulan=Februari
if "%mm%"=="03" set bulan=Maret
if "%mm%"=="04" set bulan=April
if "%mm%"=="05" set bulan=Mei
if "%mm%"=="06" set bulan=Juni
if "%mm%"=="07" set bulan=Juli
if "%mm%"=="08" set bulan=Agustus
if "%mm%"=="09" set bulan=September
if "%mm%"=="10" set bulan=Oktober
if "%mm%"=="11" set bulan=November
if "%mm%"=="12" set bulan=Desember

for /f "tokens=1-2 delims=:." %%a in ("%time%") do (
    set hh=%%a
    set mn=%%b
)

set hh=!hh: =!

echo UPDATE LAST-UPDATE >> tools\log.txt
echo !dd! !bulan! !yyyy! ^| !hh!.!mn! WIB > data\last-update-rup.txt

echo GIT CONFIG >> tools\log.txt
git config user.name "rizkipem-21"
git config user.email "rizki.pem@gmail.com"

echo GIT STATUS >> tools\log.txt
git status >> tools\log.txt 2>&1

:: FIX LOCK
del /f /q .git\index.lock >nul 2>&1

echo GIT ADD >> tools\log.txt
git add . >> tools\log.txt 2>&1

echo GIT COMMIT >> tools\log.txt
git commit -m "auto update %date% %time%" >> tools\log.txt 2>&1

echo GIT PUSH >> tools\log.txt
git push origin main >> tools\log.txt 2>&1

echo PUSH STATUS: %ERRORLEVEL% >> tools\log.txt

echo ========================= >> tools\log.txt
echo SELESAI %date% %time% >> tools\log.txt