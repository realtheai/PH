#!/usr/bin/env python3
"""
OpenAI로 뉴스 분류 (REAL_CASE/NEWS/NOISE)
"""
import requests
import json
import time
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal'
}

def classify_with_openai(text):
    """OpenAI로 분류"""
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENAI_API_KEY}"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": """당신은 피싱/스미싱 콘텐츠 분류 전문가입니다.
다음 기준으로 정확히 분류하세요:

- REAL_CASE: 실제 피싱/스미싱 문자, 카톡, 이메일 메시지 원본
- NEWS: 피싱 사건 보도, 뉴스 기사, 분석 자료
- NOISE: 피싱과 무관한 내용

JSON만 출력: {"classification": "분류"}"""
                    },
                    {
                        "role": "user",
                        "content": f"분류할 텍스트:\n{text[:1000]}"
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 50,
                "response_format": {"type": "json_object"}
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()['choices'][0]['message']['content']
            data = json.loads(result)
            classification = data.get('classification', 'ERROR')
            
            if classification in ['REAL_CASE', 'NEWS', 'NOISE']:
                return classification
            
            return 'ERROR'
        else:
            return 'ERROR'
    
    except Exception as e:
        print(f"   분류 오류: {e}")
        return 'ERROR'

def get_unclassified_news():
    """미분류 뉴스 가져오기 (최근 2일)"""
    try:
        two_days_ago = (datetime.now() - timedelta(days=2)).isoformat()
        
        url = f"{SUPABASE_URL}/rest/v1/phishing_news"
        params = {
            'select': 'id,content,translated_content',
            'classification': 'is.null',
            'crawled_at': f'gte.{two_days_ago}',
            'order': 'id.desc',
            'limit': '1000'
        }
        
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        return response.json() if response.status_code == 200 else []
    
    except Exception as e:
        print(f"DB 조회 오류: {e}")
        return []

def update_classification(record_id, classification):
    """분류 결과 업데이트"""
    try:
        url = f"{SUPABASE_URL}/rest/v1/phishing_news"
        params = {'id': f'eq.{record_id}'}
        data = {'classification': classification}
        
        response = requests.patch(url, headers=HEADERS, params=params, json=data, timeout=10)
        return response.status_code in [200, 204]
    
    except Exception:
        return False

def main():
    print(f"\n{'='*60}")
    print(f"🏷️  뉴스 분류 시작 (OpenAI gpt-4o-mini)")
    print(f"{'='*60}\n")
    
    items = get_unclassified_news()
    total = len(items)
    
    if total == 0:
        print("ℹ️  분류할 뉴스 없음")
        return
    
    print(f"📊 총 {total}개 뉴스 처리 중...\n")
    
    stats = {'REAL_CASE': 0, 'NEWS': 0, 'NOISE': 0, 'ERROR': 0}
    
    for idx, item in enumerate(items, 1):
        try:
            record_id = item['id']
            text = item.get('translated_content') or item.get('content', '')
            
            if not text or len(text.strip()) < 10:
                continue
            
            print(f"[{idx}/{total}] ID:{record_id}")
            
            # 분류
            classification = classify_with_openai(text)
            print(f"   ✅ 분류: {classification}")
            
            # 업데이트
            if update_classification(record_id, classification):
                stats[classification] += 1
                print(f"   💾 DB 업데이트 완료")
            else:
                print(f"   ⚠️  DB 업데이트 실패")
            
            if idx % 20 == 0:
                print(f"\n   진행: {idx}/{total}\n")
            
            time.sleep(0.5)
        
        except Exception as e:
            print(f"   ❌ 오류: {e}")
            continue
    
    print(f"\n{'='*60}")
    print(f"✅ 뉴스 분류 완료!")
    print(f"{'='*60}")
    print(f"   REAL_CASE: {stats['REAL_CASE']}개")
    print(f"   NEWS: {stats['NEWS']}개")
    print(f"   NOISE: {stats['NOISE']}개")
    print(f"   오류: {stats['ERROR']}개")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
