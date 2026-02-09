#!/usr/bin/env python3
"""
Solar 모델로 REAL_CASE 피싱 타입 분류
"""
import requests
import json
import time
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

HEADERS = {
    'apikey': SERVICE_KEY,
    'Authorization': f'Bearer {SERVICE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal'
}

TYPE_PROMPT = """당신은 피싱 유형 분류 전문가입니다.

다음 피싱 사례를 적절한 유형으로 분류하세요.

피싱 유형:
1. 가족사칭 - 자녀, 부모, 친척 등을 사칭
2. 공공기관사칭 - 경찰, 검찰, 금감원, 구청, 시청 등
3. 지인사칭 - 친구, 동료 등을 사칭
4. 부고/경조사 - 부고, 결혼, 돌잔치 등을 빙자
5. 정부지원금 - 코로나 지원금, 재난지원금 등
6. 금융/결제사기 - 대출, 카드, 계좌 등
7. 택배/배송사기 - CJ, 롯데택배 등 사칭
8. 투자사기 - 코인, 주식, 골드바 등
9. 기타 - 위 유형에 해당하지 않는 경우

텍스트: {text}

JSON 형식으로만 답변하세요:
{{"phishing_type": "유형 이름"}}

답변:"""

def classify_type_with_solar(text):
    """Solar 모델로 피싱 타입 분류"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "solar:10.7b",
                "prompt": TYPE_PROMPT.format(text=text[:800]),
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 100
                }
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()['response'].strip()
            
            # JSON 파싱
            try:
                if '{' in result:
                    json_str = result[result.find('{'):result.rfind('}')+1]
                    data = json.loads(json_str)
                    phishing_type = data.get('phishing_type', '기타')
                    return phishing_type
            except:
                pass
            
            # Fallback: 키워드로 판단
            keywords = {
                '가족사칭': ['가족', '자녀', '부모', '엄마', '아빠', '아들', '딸'],
                '공공기관사칭': ['경찰', '검찰', '금감원', '구청', '시청', '정부'],
                '택배/배송사기': ['택배', '배송', 'CJ', '롯데'],
                '투자사기': ['투자', '코인', '주식', '골드'],
                '금융/결제사기': ['대출', '카드', '계좌', '이체']
            }
            
            for ptype, kwds in keywords.items():
                if any(kw in result for kw in kwds):
                    return ptype
            
            return '기타'
        else:
            return '기타'
    except Exception as e:
        print(f"   ❌ Solar 오류: {str(e)[:50]}")
        return '기타'

def classify_news_phishing_type():
    """뉴스 REAL_CASE 피싱 타입 분류"""
    print("\n" + "="*80)
    print("📰 뉴스 REAL_CASE 피싱 타입 분류 (Solar)")
    print("="*80 + "\n")
    
    # REAL_CASE이고 phishing_type이 없는 뉴스 가져오기 (최근 2일)
    from datetime import datetime, timedelta
    two_days_ago = (datetime.now() - timedelta(days=2)).isoformat()
    
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/phishing_news",
        headers=HEADERS,
        params={
            'select': 'id,title,content,translated_content',
            'category': 'eq.REAL_CASE',
            'or': '(phishing_type.is.null,phishing_type.eq.)',
            'crawled_at': f'gte.{two_days_ago}',
            'limit': 500
        }
    )
    
    if response.status_code != 200:
        print(f"❌ 뉴스 조회 실패: {response.status_code}")
        return
    
    news_list = response.json()
    total = len(news_list)
    
    if total == 0:
        print("✅ 분류할 뉴스가 없습니다!")
        return
    
    print(f"📊 총 {total}개 뉴스 분류 시작...\n")
    
    stats = {}
    
    for i, news in enumerate(news_list, 1):
        title = news.get('title', '')
        content = news.get('translated_content') or news.get('content', '')
        text = f"{title}\n\n{content}"
        
        if not text.strip():
            print(f"[{i}/{total}] ID {news['id']}: ⚠️ 텍스트 없음")
            continue
        
        phishing_type = classify_type_with_solar(text)
        stats[phishing_type] = stats.get(phishing_type, 0) + 1
        
        # Supabase 업데이트
        update_resp = requests.patch(
            f"{SUPABASE_URL}/rest/v1/phishing_news",
            headers=HEADERS,
            params={'id': f"eq.{news['id']}"},
            json={'phishing_type': phishing_type}
        )
        
        if update_resp.status_code in [200, 204]:
            print(f"[{i}/{total}] ID {news['id']}: ✅ {phishing_type}")
        else:
            print(f"[{i}/{total}] ID {news['id']}: ❌ 업데이트 실패")
        
        if i % 10 == 0:
            print(f"   진행률: {i}/{total} ({i/total*100:.1f}%)")
        
        time.sleep(1)  # Solar 처리 시간
    
    print()
    print("="*80)
    print(f"✅ 뉴스 피싱 타입 분류 완료!")
    for ptype, count in stats.items():
        print(f"   {ptype}: {count}개")
    print("="*80)

def classify_images_phishing_type():
    """이미지 REAL_CASE 피싱 타입 분류"""
    print("\n" + "="*80)
    print("🖼️ 이미지 REAL_CASE 피싱 타입 분류 (Solar)")
    print("="*80 + "\n")
    
    # REAL_CASE이고 phishing_type이 없는 이미지 가져오기 (최근 2일)
    from datetime import datetime, timedelta
    two_days_ago = (datetime.now() - timedelta(days=2)).isoformat()
    
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/phishing_images",
        headers=HEADERS,
        params={
            'select': 'id,ocr_text,translated_content',
            'classification': 'eq.REAL_CASE',
            'or': '(phishing_type.is.null,phishing_type.eq.)',
            'created_at': f'gte.{two_days_ago}',
            'limit': 500
        }
    )
    
    if response.status_code != 200:
        print(f"❌ 이미지 조회 실패: {response.status_code}")
        return
    
    images_list = response.json()
    total = len(images_list)
    
    if total == 0:
        print("✅ 분류할 이미지가 없습니다!")
        return
    
    print(f"📊 총 {total}개 이미지 분류 시작...\n")
    
    stats = {}
    
    for i, img in enumerate(images_list, 1):
        text = img.get('translated_content') or img.get('ocr_text', '')
        
        if not text.strip():
            print(f"[{i}/{total}] ID {img['id']}: ⚠️ 텍스트 없음")
            continue
        
        phishing_type = classify_type_with_solar(text)
        stats[phishing_type] = stats.get(phishing_type, 0) + 1
        
        # Supabase 업데이트
        update_resp = requests.patch(
            f"{SUPABASE_URL}/rest/v1/phishing_images",
            headers=HEADERS,
            params={'id': f"eq.{img['id']}"},
            json={'phishing_type': phishing_type}
        )
        
        if update_resp.status_code in [200, 204]:
            print(f"[{i}/{total}] ID {img['id']}: ✅ {phishing_type}")
        else:
            print(f"[{i}/{total}] ID {img['id']}: ❌ 업데이트 실패")
        
        time.sleep(1)  # Solar 처리 시간
    
    print()
    print("="*80)
    print(f"✅ 이미지 피싱 타입 분류 완료!")
    for ptype, count in stats.items():
        print(f"   {ptype}: {count}개")
    print("="*80)

if __name__ == '__main__':
    print("\n🚀 Solar 피싱 타입 분류 시작\n")
    
    # 뉴스 REAL_CASE 피싱 타입 분류
    classify_news_phishing_type()
    
    # 이미지 REAL_CASE 피싱 타입 분류
    classify_images_phishing_type()
    
    print("\n✅ 전체 피싱 타입 분류 완료!\n")
