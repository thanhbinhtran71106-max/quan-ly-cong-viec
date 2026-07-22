@echo off
echo ===================================================
echo     HE THONG QUAN LY PHAN CONG CONG VIEC NHAN VIEN
echo ===================================================
echo.
echo Dang kiem tra moi truong...

:: Neu chua co venv (do tai tu GitHub ve hoac copy sang may khac)
if not exist "venv\Scripts\activate" (
    echo.
    echo [X] Phat hien ban dang chay tren may moi!
    echo [!] Dang tu dong cai dat moi truong... (Vui long doi 1-2 phut)
    python -m venv venv
    call .\venv\Scripts\activate
    echo [!] Dang tai cac thu vien can thiet...
    pip install -r requirements.txt
    echo [OK] Cai dat hoan tat!
)

echo.
echo Dang khoi dong may chu (Server)... Vui long doi giay lat...
echo (Luu y: Khong tat cua so nay trong qua trinh su dung web)
echo.

:: Mo server tren mot cua so cmd khac de no chay ngam
start "Employee Scheduler Server" cmd /k "set PYTHONHOME=&& set PYTHONPATH=&& .\venv\Scripts\activate && python run.py"

:: Doi 3 giay de server kip khoi dong
ping 127.0.0.1 -n 4 > nul

:: Tu dong mo trinh duyet web mac dinh
echo Dang mo trang web tren trinh duyet...
start http://127.0.0.1:5000

exit
