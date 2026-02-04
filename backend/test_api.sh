#!/bin/bash

# 백엔드 API 테스트 스크립트

API_URL="http://localhost:8888"

echo "====================================="
echo "피싱체커 백엔드 API 테스트"
echo "====================================="
echo ""

echo "1. 헬스체크"
curl -s $API_URL/health | python -m json.tool
echo ""
echo ""

echo "2. API 정보 조회"
curl -s $API_URL/ | python -m json.tool
echo ""
echo ""

echo "3. 위험한 메시지 분석 (예상: 80-100점)"
curl -X POST $API_URL/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"message": "긴급! 국세청입니다. 귀하의 계좌가 정지되었습니다. 본인확인을 위해 즉시 비밀번호를 입력하세요. bit.ly/xxx"}' \
  | python -m json.tool
echo ""
echo ""

echo "4. 안전한 메시지 분석 (예상: 0-20점)"
curl -X POST $API_URL/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"message": "안녕하세요. 내일 점심 약속 잡으실래요? 좋은 하루 보내세요!"}' \
  | python -m json.tool
echo ""
echo ""

echo "5. 중간 위험도 메시지 (예상: 30-50점)"
curl -X POST $API_URL/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"message": "택배가 도착했습니다. 링크를 클릭하여 확인하세요."}' \
  | python -m json.tool
echo ""
echo ""

echo "====================================="
echo "테스트 완료!"
echo "====================================="
