@echo off
echo Setting up MTG Set Generator...
echo.

REM Setup backend
echo Installing backend dependencies...
cd backend
pip install -r requirements.txt
if not exist ".env" (
    copy .env.example .env
    echo.
    echo IMPORTANT: Please edit backend\.env and add your OpenAI API key!
    echo.
)
cd ..

REM Setup frontend
echo Installing frontend dependencies...
cd frontend
call npm install
cd ..

echo.
echo Setup complete!
echo.
echo Next steps:
echo 1. Edit backend\.env and add your OpenAI API key
echo 2. Run start.bat to launch both servers
echo.
pause