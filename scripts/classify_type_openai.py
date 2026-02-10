#!/usr/bin/env python3
"""
OpenAI로 피싱 유형 분류
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

def classify_type_with_openai(text):
    """OpenAI로 피싱 유형 분류"""
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
                        "content": """당신은 피싱 유형 분류 전문가입니다.

다음 유형으로 분류하세요:
1. 가족사칭 - 자녀, 부모, 친척 사칭
2. 공공기관사칭 - 경찰, 검찰, 금감원, 구청 등
3. 지인사칭 - 친구, 동료 사칭
4. 부고/경조사 - 부고, 결혼, 돌잔치 빙자
5. 정부지원금 - 코로나 지원금, 재난지원금
6. 금융/결제사기 - 대출, 카드, 계좌
7. 택배/배송사기 - CJ, 롯데택배 사칭
8. 투자사기 - 코인, 주식, 골드바
9. 기타 - 위 유형에 해당하지 않음

JSON만 출력: {"phishing_type": "유형"}"""
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
            phishing_type = data.get('phishing_type', '기타')
            return phishing_type
        else:
            return '기타'
    
    except Exception as e:
        print(f"   분류 오류: {e}")
        return '기타'

def get_untyped_items():
    """유형 미분류 REAL_CASE 가져오기 (최근 2일, news+images)"""
    items = []
    
    try:
        two_days_ago = (datetime.now() - timedelta(days=2)).isoformat()
        
        # 뉴스
        url_news = f"{SUPABASE_URL}/rest/v1/phishing_news"
        params_news = {
            'select': 'id,content,translated_content',
            'classification': 'eq.REAL_CASE',
            'phishing_type': 'is.null',
            'crawled_at': f'gte.{two_days_ago}',
            'order': 'id.desc',
            'limit': '500'
        }
        
        response = requests.get(url_news, headers=HEADERS, params=params_news, timeout=10)
        if response.status_code == 200:
            for item in response.json():
                items.append(('news', item))
        
        # 이미지
        url_images = f"{SUPABASE_URL}/rest/v1/phishing_images"
        params_images = {
            'select': 'id,extracted_text',
            'classification': 'eq.REAL_CASE',
            'phishing_type': 'is.null',
            'crawled_at': f'gte.{two_days_ago}',
            'order': 'id.desc',
            'limit': '500'
        }
        
        response = requests.get(url_images, headers=HEADERS, params=params_images, timeout=10)
        if response.status_code == 200:
            for item in response.json():
                items.append(('images', item))
        
        return items
    
    except Exception as e:
        print(f"DB 조회 오류: {e}")
        return []

def update_phishing_type(table, record_id, phishing_type):
    """유형 업데이트"""
    try:
        table_name = 'phishing_news' if table == 'news' else 'phishing_images'
        url = f"{SUPABASE_URL}/rest/v1/{table_name}"
        params = {'id': f'eq.{record_id}'}
        data = {'phishing_type': phishing_type}
        
        response = requests.patch(url, headers=HEADERS, params=params, json=data, timeout=10)
        return response.status_code in [200, 204]
    
    except Exception:
        return False

def main():
    print(f"\n{'='*60}")
    print(f"🎯 피싱 유형 분류 시작 (OpenAI gpt-4o-mini)")
    print(f"{'='*60}\n")
    
    items = get_untyped_items()
    total = len(items)
    
    if total == 0:
        print("ℹ️  분류할 항목 없음")
        return
    
    print(f"📊 총 {total}개 항목 처리 중...\n")
    
    stats = {}
    success = 0
    
    for idx, (table, item) in enumerate(items, 1):
        try:
            record_id = item['id']
            
            if table == 'news':
                text = item.get('translated_content') or item.get('content', '')
            else:
                text = item.get('extracted_text', '')
            
            if not text or len(text.strip()) < 10:
                continue
            
            print(f"[{idx}/{total}] {table.upper()} ID:{record_id}")
            
            # 분류
            phishing_type = classify_type_with_openai(text)
            print(f"   ✅ 유형: {phishing_type}")
            
            # 업데이트
            if update_phishing_type(table, record_id, phishing_type):
                stats[phishing_type] = stats.get(phishing_type, 0) + 1
                success += 1
                print(f"   💾 DB 업데이트 완료")
            else:
                print(f"   ⚠️  DB 업데이트 실패")
            
            if idx % 20 == 0:
                print(f"\n   진행: {idx}/{total} (성공:{success})\n")
            
            time.sleep(0.5)
        
        except Exception as e:
            print(f"   ❌ 오류: {e}")
            continue
    
    print(f"\n{'='*60}")
    print(f"✅ 피싱 유형 분류 완료!")
    print(f"{'='*60}")
    print(f"   총 성공: {success}개")
    print(f"\n   유형별 통계:")
    for phishing_type, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
        print(f"   - {phishing_type}: {count}개")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
