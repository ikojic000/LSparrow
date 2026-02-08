@echo off
echo Starting CSV Statistics Calculator...
echo.

cd /d "C:\Users\IvanK\Python Projects\DiplomskiCSVStatistika"
call "C:\Users\IvanK\Python Projects\Virtual ENVs\Diplomski_CSV_Statistics\Scripts\activate.bat"

echo Virtual environment activated.
echo Starting Flask server at http://127.0.0.1:5000
echo Press Ctrl+C to stop the server.
echo.

python run.py

pause
