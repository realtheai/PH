#!/usr/bin/env python3
"""
Solar 모델로 분류 (REAL_CASE/NEWS/NOISE)
"""
import requests
import json
import time
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

HEADERS = {
    'apikey': SERVICE_KEY,
    'Authorization': f'Bearer {SERVICE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal'
}

CLASSIFY_PROMPT = """다음 텍스트를 분석하여 피싱/스미싱 관련성을 판단하세요.

분류 기준:
- REAL_CASE: 실제 피싱/스미싱 문자나 메시지 (문자, 카톡, 이메일 등)
- NEWS: 피싱 관련 뉴스 기사나 보도자료
- NOISE: 피싱과 관련 없는 내용

텍스트: {text}

JSON 형식으로만 답변하세요:
{{"classification": "REAL_CASE"}}
또는
{{"classification": "NEWS"}}
또는
{{"classification": "NOISE"}}

답변:"""

def classify_with_solar(text):
    """Solar 모델로 분류"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "solar:10.7b",
                "prompt": CLASSIFY_PROMPT.format(text=text[:500]),
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 50
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
                    classification = data.get('classification', 'ERROR')
                    
                    if classification in ['REAL_CASE', 'NEWS', 'NOISE']:
                        return classification
            except:
                pass
            
            # Fallback: 키워드로 판단
            if 'REAL_CASE' in result:
                return 'REAL_CASE'
            elif 'NEWS' in result:
                return 'NEWS'
            elif 'NOISE' in result:
                return 'NOISE'
            
            return 'ERROR'
        else:
            return 'ERROR'
    except Exception as e:
        print(f"   ❌ Solar 오류: {str(e)[:50]}")
        return 'ERROR'

def classify_news():
    """뉴스 분류"""
    print("\n" + "="*80)
    print("📰 뉴스 분류 (Solar)")
    print("="*80 + "\n")
    
    # category가 없는 뉴스 가져오기
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/phishing_news",
        headers=HEADERS,
        params={
            'select': 'id,title,content,translated_content',
            'or': '(category.is.null,category.eq.)',
            'limit': 1000
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
    
    stats = {'REAL_CASE': 0, 'NEWS': 0, 'NOISE': 0, 'ERROR': 0}
    
    for i, news in enumerate(news_list, 1):
        text = news.get('translated_content') or news.get('content') or news.get('title', '')
        
        if not text:
            print(f"[{i}/{total}] ID {news['id']}: ⚠️ 텍스트 없음")
            continue
        
        classification = classify_with_solar(text)
        stats[classification] += 1
        
        if classification != 'ERROR':
            # Supabase 업데이트
            update_resp = requests.patch(
                f"{SUPABASE_URL}/rest/v1/phishing_news",
                headers=HEADERS,
                params={'id': f"eq.{news['id']}"},
                json={'category': classification}
            )
            
            if update_resp.status_code in [200, 204]:
                print(f"[{i}/{total}] ID {news['id']}: ✅ {classification}")
            else:
                print(f"[{i}/{total}] ID {news['id']}: ❌ 업데이트 실패")
        else:
            print(f"[{i}/{total}] ID {news['id']}: ❌ 분류 실패")
        
        time.sleep(0.1)
    
    print()
    print("="*80)
    print(f"✅ 뉴스 분류 완료!")
    print(f"   REAL_CASE: {stats['REAL_CASE']}개")
    print(f"   NEWS: {stats['NEWS']}개")
    print(f"   NOISE: {stats['NOISE']}개")
    print(f"   ERROR: {stats['ERROR']}개")
    print("="*80)

def classify_images():
    """이미지 분류"""
    print("\n" + "="*80)
    print("🖼️ 이미지 분류 (Solar)")
    print("="*80 + "\n")
    
    # classification이 없는 이미지 가져오기
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/phishing_images",
        headers=HEADERS,
        params={
            'select': 'id,ocr_text,translated_content',
            'or': '(classification.is.null,classification.eq.)',
            'limit': 1000
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
    
    stats = {'REAL_CASE': 0, 'NEWS': 0, 'NOISE': 0, 'ERROR': 0}
    
    for i, img in enumerate(images_list, 1):
        text = img.get('translated_content') or img.get('ocr_text', '')
        
        if not text:
            print(f"[{i}/{total}] ID {img['id']}: ⚠️ 텍스트 없음")
            continue
        
        classification = classify_with_solar(text)
        stats[classification] += 1
        
        if classification != 'ERROR':
            # Supabase 업데이트
            update_resp = requests.patch(
                f"{SUPABASE_URL}/rest/v1/phishing_images",
                headers=HEADERS,
                params={'id': f"eq.{img['id']}"},
                json={'classification': classification}
            )
            
            if update_resp.status_code in [200, 204]:
                print(f"[{i}/{total}] ID {img['id']}: ✅ {classification}")
            else:
                print(f"[{i}/{total}] ID {img['id']}: ❌ 업데이트 실패")
        else:
            print(f"[{i}/{total}] ID {img['id']}: ❌ 분류 실패")
        
        if i % 10 == 0:
            print(f"   진행률: {i}/{total} ({i/total*100:.1f}%)")
        
        time.sleep(0.1)
    
    print()
    print("="*80)
    print(f"✅ 이미지 분류 완료!")
    print(f"   REAL_CASE: {stats['REAL_CASE']}개")
    print(f"   NEWS: {stats['NEWS']}개")
    print(f"   NOISE: {stats['NOISE']}개")
    print(f"   ERROR: {stats['ERROR']}개")
    print("="*80)

if __name__ == '__main__':
    print("\n🚀 Solar 모델 분류 시작")
    classify_news()
    classify_images()
    print("\n✅ 전체 분류 완료!\n")
