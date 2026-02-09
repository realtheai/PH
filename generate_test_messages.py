#!/usr/bin/env python3
"""
실제 REAL_CASE에서 테스트용 메시지 추출 (다양한 유형)
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
print("📋 실제 피싱 메시지 테스트 샘플 (벡터 검색 확인용)")
print("="*100 + "\n")

# REAL_CASE 이미지에서 다양한 길이와 유형 추출
response = requests.get(
    f"{supabase_url}/rest/v1/phishing_images",
    headers=headers,
    params={
        'select': 'id,ocr_text,text_length',
        'classification': 'eq.REAL_CASE',
        'ocr_text': 'not.is.null',
        'order': 'text_length.desc',
        'limit': 200
    },
    timeout=30
)

if response.status_code != 200:
    print(f"❌ 데이터 조회 실패: {response.status_code}")
    exit(1)

data = response.json()

# 카테고리별 샘플
categories = {
    '🚚 택배/배송': ['택배', '배송', '소포', '반송', 'cj', '우체국', 'delivery', 'package', 'fedex'],
    '💳 금융/카드': ['은행', '카드', '계좌', '본인인증', '보안', 'bank', 'card', 'account'],
    '👨‍👩‍👧 가족사칭': ['엄마', '아빠', '엄마야', '아빠야', '휴대폰', '폰고장', '번호'],
    '🏢 공공기관': ['국세청', '경찰', '검찰', '법원', '세무서', '우체국', 'irs', 'police'],
    '💌 청첩장/부고': ['청첩장', '결혼', '부고', '별세', '조문', 'wedding'],
    '📱 문자링크': ['http', 'https', 'bit.ly', 'goo.gl', 'tinyurl', '.com/', 'link'],
}

samples = []
used_texts = set()

for category, keywords in categories.items():
    category_samples = []
    
    for item in data:
        text = item['ocr_text'].strip()
        text_lower = text.lower()
        
        # 이미 사용한 텍스트는 스킵
        if text in used_texts:
            continue
        
        # 너무 짧거나 긴 것 제외
        if len(text) < 20 or len(text) > 300:
            continue
        
        # 키워드 매칭
        if any(kw in text_lower for kw in keywords):
            category_samples.append({
                'category': category,
                'text': text,
                'length': len(text),
                'id': item['id']
            })
            used_texts.add(text)
            
            if len(category_samples) >= 2:
                break
    
    samples.extend(category_samples)

# 출력
print(f"총 {len(samples)}개의 다양한 피싱 메시지 샘플\n")

count = 1
current_category = None

for sample in samples:
    category = sample['category']
    
    if category != current_category:
        print(f"\n{'='*100}")
        print(f"{category}")
        print(f"{'='*100}\n")
        current_category = category
    
    text = sample['text']
    print(f"[테스트 {count}] (길이: {sample['length']}자)")
    print(f"─" * 100)
    print(text)
    print(f"─" * 100)
    print()
    count += 1

# 추가: 정상 메시지 대조군
print(f"\n{'='*100}")
print("✅ 정상 메시지 (대조군)")
print(f"{'='*100}\n")

normal_messages = [
    "내일 오후 3시에 강남역 2번 출구에서 만나요. 점심 먹고 영화 보는 거 잊지 마세요!",
    "회의 자료 잘 받았습니다. 검토 후 내일 오전까지 피드백 드리겠습니다.",
    "주말에 날씨 좋다는데 등산 갈까요? 북한산 어때요?",
    "생일 축하해! 저녁에 파티 준비해놨어. 7시까지 와!",
]

for i, msg in enumerate(normal_messages, count):
    print(f"[테스트 {i}] (길이: {len(msg)}자)")
    print(f"─" * 100)
    print(msg)
    print(f"─" * 100)
    print()

print("="*100)
print("💡 테스트 방법:")
print("   1. http://localhost:3000 접속")
print("   2. 위 메시지 중 하나 복사")
print("   3. 입력창에 붙여넣기")
print("   4. '검사하기' 클릭")
print("   5. 결과 확인:")
print("      - 위험도 점수")
print("      - 유사 피싱 사례 개수")
print("      - AI 분석 결과")
print("="*100 + "\n")
