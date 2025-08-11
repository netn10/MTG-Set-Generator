@echo off
echo Starting MTG Set Generator...
echo.

REM Start backend in new window
echo Starting Flask backend...
start "MTG Backend" cmd /k "cd backend && python app.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak > nul

REM Start frontend in new window
echo Starting React frontend...
start "MTG Frontend" cmd /k "cd frontend && npm start"

echo.
echo Both servers are starting...
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Press any key to exit...
pause > nul