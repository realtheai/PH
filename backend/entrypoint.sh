#!/bin/bash
set -e

# Railway PORT 환경변수 처리
if [ -z "$PORT" ]; then
    echo "⚠️  PORT 환경변수가 없습니다. 기본값 8000 사용"
    export PORT=8000
fi

echo "🚀 Starting uvicorn on port $PORT..."
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
