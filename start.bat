@echo off
echo Starting LSparrow...
echo.

cd /d "C:\Users\IvanK\Python Projects\LSparrow"
call "C:\Users\IvanK\Python Projects\Virtual ENVs\LSparrow\Scripts\activate.bat"

echo Virtual environment activated.
echo Starting Flask server at http://127.0.0.1:5000
echo Press Ctrl+C to stop the server.
echo.

python run.py

pause
