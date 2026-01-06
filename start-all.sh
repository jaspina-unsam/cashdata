#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to cleanup processes on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down services...${NC}"
    
    if [ ! -z "$BACKEND_PID" ]; then
        echo -e "${BLUE}Stopping backend (PID: $BACKEND_PID)${NC}"
        kill $BACKEND_PID 2>/dev/null
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        echo -e "${BLUE}Stopping frontend (PID: $FRONTEND_PID)${NC}"
        kill $FRONTEND_PID 2>/dev/null
    fi
    
    echo -e "${GREEN}All services stopped${NC}"
    exit 0
}

# Set up trap to catch Ctrl+C and other termination signals
trap cleanup SIGINT SIGTERM

# Check if backend directory exists
if [ ! -d "backend" ]; then
    echo -e "${RED}Error: backend directory not found${NC}"
    exit 1
fi

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
    echo -e "${RED}Error: frontend directory not found${NC}"
    exit 1
fi

echo -e "${GREEN}🚀 Starting CashData services...${NC}\n"

# Start backend
echo -e "${BLUE}Starting backend server...${NC}"
cd backend
poetry run uvicorn app.infrastructure.api.main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 2

# Check if backend started successfully
if kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID) - http://localhost:8000${NC}"
else
    echo -e "${RED}✗ Backend failed to start. Check backend.log for details${NC}"
    exit 1
fi

# Start frontend
echo -e "${BLUE}Starting frontend server...${NC}"
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait a moment for frontend to start
sleep 3

# Check if frontend started successfully
if kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID) - http://localhost:5173${NC}"
else
    echo -e "${RED}✗ Frontend failed to start. Check frontend.log for details${NC}"
    cleanup
    exit 1
fi

echo -e "\n${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  All services are running!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Backend:  ${NC}http://localhost:8000"
echo -e "${BLUE}  Frontend: ${NC}http://localhost:5173"
echo -e "${BLUE}  API Docs: ${NC}http://localhost:8000/docs"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "\n${YELLOW}Logs are being written to:${NC}"
echo -e "  - backend.log"
echo -e "  - frontend.log"
echo -e "\n${YELLOW}Press Ctrl+C to stop all services${NC}\n"

# Keep script running and show logs
tail -f backend.log frontend.log
