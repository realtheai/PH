#!/usr/bin/env python3
"""
벡터 검색 직접 테스트 (Supabase RPC)
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
print("🧪 Supabase 벡터 검색 직접 테스트")
print("="*100 + "\n")

# 1. 실제 데이터에서 임베딩 하나 가져오기
print("1️⃣ 테스트용 임베딩 가져오는 중...\n")

response = requests.get(
    f"{supabase_url}/rest/v1/phishing_images",
    headers=headers,
    params={
        'select': 'id,ocr_text,embedding',
        'classification': 'eq.REAL_CASE',
        'embedding': 'not.is.null',
        'limit': 1
    },
    timeout=10
)

if response.status_code != 200:
    print(f"❌ 데이터 조회 실패: {response.status_code}")
    exit(1)

data = response.json()
if not data:
    print("❌ 데이터가 없습니다")
    exit(1)

test_item = data[0]
test_embedding = test_item['embedding']
test_text = test_item['ocr_text'][:100]

print(f"✅ 테스트 데이터:")
print(f"   ID: {test_item['id']}")
print(f"   텍스트: {test_text}...")
print(f"   임베딩 차원: {len(test_embedding)}\n")

# 2. RPC 함수 호출
print("2️⃣ find_similar_phishing 함수 호출 중...\n")

rpc_url = f"{supabase_url}/rest/v1/rpc/find_similar_phishing"
payload = {
    'query_embedding': test_embedding,
    'match_threshold': 0.5,
    'match_count': 5
}

response = requests.post(rpc_url, headers=headers, json=payload, timeout=30)

print(f"📡 응답 코드: {response.status_code}")

if response.status_code == 200:
    results = response.json()
    print(f"✅ 검색 성공! {len(results)}건 발견\n")
    
    print("="*100)
    print("🔍 검색 결과")
    print("="*100 + "\n")
    
    for idx, result in enumerate(results[:5], 1):
        print(f"[{idx}] 유사도: {result['similarity']:.4f}")
        print(f"    타입: {result['source_type']}")
        print(f"    ID: {result['id']}")
        if result.get('title'):
            print(f"    제목: {result['title']}")
        content = result.get('content', '')[:100]
        print(f"    내용: {content}...")
        print()
else:
    print(f"❌ 검색 실패")
    print(f"   응답: {response.text}\n")

print("="*100 + "\n")
