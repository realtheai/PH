#!/usr/bin/env python3
"""
오늘 크롤링한 이미지만 분류
"""
import os
import sys
import requests
import json
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
OPENAI_KEY = os.getenv('OPENAI_API_KEY')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

# 오늘 날짜
today = datetime.utcnow().strftime('%Y-%m-%d')

print(f"\n🔍 오늘({today}) 크롤링한 이미지 분류 시작...\n")

# 1. 오늘 이미지 조회 (OCR은 있지만 classification이 없는 것)
url = f"{SUPABASE_URL}/rest/v1/phishing_images"
params = {
    'select': 'id,ocr_text',
    'created_at': f'gte.{today}',
    'classification': 'is.null',
    'ocr_text': 'not.is.null',
    'limit': 1000
}

response = requests.get(url, headers=HEADERS, params=params)
images = response.json()

print(f"📸 분류할 이미지: {len(images)}개\n")

if not images:
    print("✅ 분류할 이미지가 없습니다!")
    sys.exit(0)

# 분류 프롬프트 (간단 버전)
CLASSIFY_PROMPT = """다음 OCR 텍스트를 분석하여 피싱/스미싱 관련성을 판단하세요.

REAL_CASE: 실제 피싱 사례 (문자, 카톡 등)
NEWS: 피싱 뉴스/기사  
NOISE: 관련 없음

JSON으로만 답변:
{"classification": "REAL_CASE|NEWS|NOISE", "reason": "이유"}

텍스트: {text}"""

# 2. 분류 시작
success = 0
failed = 0

for i, img in enumerate(images, 1):
    img_id = img['id']
    ocr_text = img['ocr_text'][:500]  # 처음 500자만
    
    print(f"[{i}/{len(images)}] ID:{img_id}")
    
    try:
        # OpenAI API 호출
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {OPENAI_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'gpt-4o-mini',
                'messages': [
                    {'role': 'system', 'content': '피싱 분류 전문가'},
                    {'role': 'user', 'content': CLASSIFY_PROMPT.format(text=ocr_text)}
                ],
                'temperature': 0.3
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # JSON 파싱
            try:
                data = json.loads(content)
                classification = data.get('classification', 'NOISE')
            except:
                classification = 'NOISE'
            
            # DB 업데이트
            update_url = f"{SUPABASE_URL}/rest/v1/phishing_images?id=eq.{img_id}"
            update_response = requests.patch(
                update_url,
                headers=HEADERS,
                json={'classification': classification}
            )
            
            if update_response.status_code in [200, 204]:
                print(f"   ✅ {classification}")
                success += 1
            else:
                print(f"   ❌ DB 업데이트 실패")
                failed += 1
        else:
            print(f"   ⚠️  API 실패: {response.status_code}")
            failed += 1
            time.sleep(1)
    
    except Exception as e:
        print(f"   ❌ 에러: {str(e)[:50]}")
        failed += 1
    
    # Rate limit 관리
    if i % 10 == 0:
        time.sleep(1)

print(f"\n✅ 완료: {success}개 | ❌ 실패: {failed}개\n")
