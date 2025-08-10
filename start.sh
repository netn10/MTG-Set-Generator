#!/bin/bash

echo "Starting MTG Set Generator..."
echo

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo "ERROR: backend/.env file not found!"
    echo "Please copy backend/.env.example to backend/.env and add your OpenAI API key"
    exit 1
fi

# Function to cleanup background processes
cleanup() {
    echo "Shutting down servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Start backend
echo "Starting Flask backend..."
cd backend
python app.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo "Starting React frontend..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo
echo "Both servers are running:"
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:3000"
echo
echo "Press Ctrl+C to stop both servers"

# Wait for user to stop
wait