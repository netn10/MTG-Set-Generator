#!/bin/bash

echo "Setting up MTG Set Generator..."
echo

# Setup backend
echo "Installing backend dependencies..."
cd backend
pip install -r requirements.txt
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo
    echo "IMPORTANT: Please edit backend/.env and add your OpenAI API key!"
    echo
fi
cd ..

# Setup frontend
echo "Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo
echo "Setup complete!"
echo
echo "Next steps:"
echo "1. Edit backend/.env and add your OpenAI API key"
echo "2. Run ./start.sh to launch both servers"
echo

# Make start script executable
chmod +x start.sh