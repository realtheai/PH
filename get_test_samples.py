#!/usr/bin/env python3
"""
실제 REAL_CASE 피싱 메시지 샘플 추출
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_ANON_KEY')

headers = {
    'apikey': supabase_key,
    'Authorization': f'Bearer {supabase_key}',
    'Content-Type': 'application/json'
}

print("\n" + "="*100)
print("📋 실제 피싱 메시지 테스트 샘플 (REAL_CASE)")
print("="*100 + "\n")

# REAL_CASE 이미지에서 다양한 유형 추출
response = requests.get(
    f"{supabase_url}/rest/v1/phishing_images",
    headers=headers,
    params={
        'select': 'id,ocr_text,phishing_type,classification',
        'classification': 'eq.REAL_CASE',
        'ocr_text': 'not.is.null',
        'limit': 100
    },
    timeout=30
)

if response.status_code != 200:
    print(f"❌ 데이터 조회 실패: {response.status_code}")
    exit(1)

data = response.json()

# 다양한 유형별로 샘플링
samples = {
    '택배/배송 사기': [],
    '금융/기관 사칭': [],
    '가족/지인 사칭': [],
    '청첩장/부고 스미싱': [],
    '기타 피싱': []
}

# 키워드로 분류
for item in data:
    text = item['ocr_text'].lower()
    
    if any(kw in text for kw in ['택배', '배송', '소포', '반송', 'cj', '우체국', 'delivery']):
        if len(samples['택배/배송 사기']) < 3:
            samples['택배/배송 사기'].append(item)
    elif any(kw in text for kw in ['은행', '카드', '계좌', '본인인증', '보안', '비밀번호', 'bank', 'card']):
        if len(samples['금융/기관 사칭']) < 3:
            samples['금융/기관 사칭'].append(item)
    elif any(kw in text for kw in ['엄마', '아빠', '팀장', '사장', '부장', '휴대폰']):
        if len(samples['가족/지인 사칭']) < 3:
            samples['가족/지인 사칭'].append(item)
    elif any(kw in text for kw in ['청첩장', '부고', '결혼', '조문']):
        if len(samples['청첩장/부고 스미싱']) < 2:
            samples['청첩장/부고 스미싱'].append(item)
    else:
        if len(samples['기타 피싱']) < 2:
            samples['기타 피싱'].append(item)

# 출력
count = 1
for category, items in samples.items():
    if not items:
        continue
    
    print(f"\n{'='*100}")
    print(f"🎯 {category}")
    print(f"{'='*100}\n")
    
    for item in items:
        text = item['ocr_text'].strip()
        # 너무 긴 텍스트는 자르기
        if len(text) > 200:
            text = text[:200] + "..."
        
        print(f"[예시 {count}]")
        print(f"─" * 100)
        print(text)
        print(f"─" * 100)
        print()
        count += 1

print("="*100)
print("💡 사용 방법:")
print("   1. 브라우저에서 http://localhost:3000 접속")
print("   2. 위 메시지 중 하나를 복사")
print("   3. 텍스트 입력 창에 붙여넣기")
print("   4. '검사하기' 버튼 클릭")
print("   5. AI 분석 결과 확인!")
print("="*100 + "\n")
