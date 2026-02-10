#!/bin/bash
set -e

# Railway PORT 환경변수 처리
if [ -z "$PORT" ]; then
    echo "⚠️  PORT not set, using default 8000"
    PORT=8000
else
    echo "✅ PORT set to $PORT"
fi

echo "🚀 Starting uvicorn on 0.0.0.0:$PORT..."
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
