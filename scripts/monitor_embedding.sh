#!/bin/bash
# 임베딩 진행 상황 모니터링

echo "🔍 임베딩 생성 모니터링 시작..."
echo "Ctrl+C로 종료하세요"
echo ""

while true; do
    clear
    date "+%Y-%m-%d %H:%M:%S"
    echo ""
    python scripts/check_progress.py
    echo ""
    echo "30초 후 다시 확인..."
    sleep 30
done
