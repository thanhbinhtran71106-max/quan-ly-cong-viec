@echo off
echo ===================================================
echo     HE THONG QUAN LY PHAN CONG CONG VIEC NHAN VIEN
echo ===================================================
echo.
echo Dang khoi dong may chu (Server)... Vui long doi giay lat...
echo (Luu y: Khong tat cua so nay trong qua trinh su dung web)
echo.

:: Mo server tren mot cua so cmd khac de no chay ngam (hoac chay truc tiep)
start "Employee Scheduler Server" cmd /k "set PYTHONHOME=&& set PYTHONPATH=&& .\venv\Scripts\activate && python run.py"

:: Doi 3 giay de server kip khoi dong
ping 127.0.0.1 -n 4 > nul

:: Tu dong mo trinh duyet web mac dinh
echo Dang mo trang web tren trinh duyet...
start http://127.0.0.1:5000

exit
