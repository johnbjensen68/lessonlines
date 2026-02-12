#!/bin/bash

# LessonLines Remote Development Server Startup Script
# This script starts both backend and frontend servers accessible remotely

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting LessonLines Development Servers${NC}"
echo "==========================================="

# Get the machine's IP address
IP_ADDR=$(hostname -I | awk '{print $1}')

# Start backend
echo -e "${YELLOW}Starting backend server...${NC}"
cd "$PROJECT_DIR/backend"

if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Creating virtual environment..."
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

# Start backend in background, binding to all interfaces
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start frontend
echo -e "${YELLOW}Starting frontend server...${NC}"
cd "$PROJECT_DIR/frontend"

if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Start frontend with host flag for remote access
npm run dev -- --host &
FRONTEND_PID=$!

echo ""
echo -e "${GREEN}Servers started!${NC}"
echo "==========================================="
echo -e "Backend API:  http://${IP_ADDR}:8000"
echo -e "Frontend UI:  http://${IP_ADDR}:5173"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Trap Ctrl+C to kill both processes
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down servers...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for both processes
wait
