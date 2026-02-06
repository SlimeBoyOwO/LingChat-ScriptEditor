:: Start backend and frontend simultaneously
@echo off
echo Starting LingChat Script Editor...

:: Start backend
start "Backend Server" cmd /k "cd backend && uvicorn src.main:app --reload"

:: Start frontend
start "Frontend Server" cmd /k "cd frontend && pnpm run dev"

echo Both servers are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5174
pause
