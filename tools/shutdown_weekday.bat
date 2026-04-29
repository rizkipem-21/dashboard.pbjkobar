@echo off

echo Komputer akan shutdown dalam 5 menit...
echo Tekan tombol apapun untuk membatalkan...

shutdown /s /t 300

timeout /t 300 >nul

shutdown -a
echo Shutdown dibatalkan
pause