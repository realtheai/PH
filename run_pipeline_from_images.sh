#!/bin/bash
# 이미지 크롤링부터 재개

set -e
cd /home/realtheai/phishingapp

echo "=========================================="
echo "🚀 파이프라인 재개 (이미지부터)"
echo "=========================================="

echo "  🕷️ [3/5] 구글 이미지 크롤링..."
python3 -u scripts/daily_google_images.py

echo "  🕷️ [4/5] Reddit 크롤링..."
python3 -u scripts/daily_reddit.py

echo "  🕷️ [5/5] 해외 뉴스 크롤링..."
python3 -u scripts/daily_international.py

echo "📊 [2/7] 이미지 OCR 처리 (최근 2일)..."
python3 -u scripts/process_recent_images_ocr.py

echo "📊 [3/7] 콘텐츠 분류..."
python3 -u scripts/classify_images_openai.py
python3 -u scripts/classify_news_openai.py

echo "📊 [4/7] 피싱 유형 분류..."
python3 -u scripts/classify_type_openai.py

echo "📊 [5/7] 중복 제거..."
python3 -u scripts/deduplicate_data.py

echo "📊 [6/7] 번역..."
python3 -u scripts/translate_all_content.py

echo "📊 [7/7] 임베딩..."
python3 -u scripts/embed_with_openai.py

echo "🎉 파이프라인 완료!"
