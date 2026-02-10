#!/bin/bash
# Railway 시작 스크립트

# PORT 환경변수가 없으면 8000 사용
PORT=${PORT:-8000}

echo "Starting uvicorn on port $PORT..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
