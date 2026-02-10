#!/bin/bash
# 전체 데이터 파이프라인 실행 스크립트 (GitHub Actions와 동일)

set -e  # 오류 발생 시 중단

echo "=========================================="
echo "🚀 피싱 데이터 파이프라인 시작"
echo "=========================================="
echo ""

# 시작 시간
START_TIME=$(date +%s)

# 1단계: 크롤링 (병렬 실행 가능, 하지만 순차로 실행)
echo "📊 [1/7] 크롤링 단계 시작..."
echo ""

echo "  🕷️ [1/5] 네이버 API 크롤링..."
cd /home/realtheai/phishingapp
python3 -u scripts/daily_naver.py
echo "  ✅ 네이버 완료"
echo ""

echo "  🕷️ [2/5] 구글 뉴스 크롤링..."
python3 -u scripts/daily_google.py
echo "  ✅ 구글 뉴스 완료"
echo ""

echo "  🕷️ [3/5] 구글 이미지 크롤링..."
python3 -u scripts/daily_google_images.py
echo "  ✅ 구글 이미지 완료"
echo ""

echo "  🕷️ [4/5] Reddit 크롤링..."
python3 -u scripts/daily_reddit.py
echo "  ✅ Reddit 완료"
echo ""

echo "  🕷️ [5/5] 해외 뉴스 크롤링..."
python3 -u scripts/daily_international.py
echo "  ✅ 해외 뉴스 완료"
echo ""

# 2단계: OCR 처리
echo "📊 [2/7] 이미지 OCR 처리 (최근 2일)..."
python3 -u scripts/process_recent_images_ocr.py
echo "  ✅ OCR 완료"
echo ""

# 3단계: 콘텐츠 분류
echo "📊 [3/7] 콘텐츠 분류 (REAL_CASE/NEWS/NOISE)..."
python3 -u scripts/classify_images_openai.py
python3 -u scripts/classify_news_openai.py
echo "  ✅ 분류 완료"
echo ""

# 4단계: 피싱 유형 분류
echo "📊 [4/7] 피싱 유형 분류..."
python3 -u scripts/classify_type_openai.py
echo "  ✅ 유형 분류 완료"
echo ""

# 5단계: 중복 제거
echo "📊 [5/7] 중복 제거 (번역 전)..."
python3 -u scripts/deduplicate_data.py
echo "  ✅ 중복 제거 완료"
echo ""

# 6단계: 번역
echo "📊 [6/7] 텍스트 번역 (영어→한국어)..."
python3 -u scripts/translate_all_content.py
echo "  ✅ 번역 완료"
echo ""

# 7단계: 벡터 임베딩
echo "📊 [7/7] 벡터 임베딩 생성..."
python3 -u scripts/embed_with_openai.py
echo "  ✅ 임베딩 완료"
echo ""

# 종료 시간
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
MINUTES=$((DURATION / 60))
SECONDS=$((DURATION % 60))

echo ""
echo "=========================================="
echo "🎉 파이프라인 완료!"
echo "⏱️  소요 시간: ${MINUTES}분 ${SECONDS}초"
echo "=========================================="
