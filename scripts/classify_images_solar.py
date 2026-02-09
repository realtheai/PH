#!/usr/bin/env python3
"""
이미지 분류 (Solar 모델) - OCR 완료된 이미지 대상
REAL_CASE / NEWS / NOISE 분류
"""
import os
import requests
import json
from dotenv import load_dotenv
import time

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

# Solar 분류 프롬프트
CLASSIFICATION_PROMPT = """다음 텍스트가 실제 피싱 사례인지, 단순 뉴스 기사인지, 또는 관련 없는 노이즈인지 분류해주세요.

텍스트:
{text}

분류 기준:
- REAL_CASE: 실제 피싱/스미싱 메시지, 사기 문자, 실제 피해 사례 스크린샷
- NEWS: 피싱 관련 뉴스 기사, 보도 자료, 안내문
- NOISE: 피싱과 무관한 내용, 광고, 일반 문자

JSON 형식으로만 답변:
{{"classification": "REAL_CASE" or "NEWS" or "NOISE"}}"""

def classify_with_solar(text):
    """Solar 모델로 분류"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "solar:10.7b",
                "prompt": CLASSIFICATION_PROMPT.format(text=text[:1000]),
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 50
                }
            },
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            text_response = result.get('response', '').strip()
            
            # JSON 파싱
            try:
                # JSON 블록 추출
                if '```json' in text_response:
                    json_text = text_response.split('```json')[1].split('```')[0].strip()
                elif '```' in text_response:
                    json_text = text_response.split('```')[1].split('```')[0].strip()
                else:
                    json_text = text_response
                
                parsed = json.loads(json_text)
                classification = parsed.get('classification', 'NOISE')
                
                # 유효성 검사
                if classification in ['REAL_CASE', 'NEWS', 'NOISE']:
                    return classification
                else:
                    return 'NOISE'
            except:
                # JSON 파싱 실패 시 키워드 검색
                text_lower = text_response.lower()
                if 'real_case' in text_lower:
                    return 'REAL_CASE'
                elif 'news' in text_lower:
                    return 'NEWS'
                else:
                    return 'NOISE'
        
        return 'NOISE'
    
    except Exception as e:
        print(f"      Solar 에러: {e}")
        return 'NOISE'

def classify_images():
    """OCR 완료된 이미지 분류"""
    
    print("\n" + "="*100)
    print("🚀 이미지 분류 시작 (Solar 모델)")
    print("="*100 + "\n")
    
    # OCR 완료 + 분류 안 된 이미지 조회
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/phishing_images?select=id,ocr_text,translated_text&ocr_text=not.is.null&classification=is.null&limit=1000",
        headers=headers,
        timeout=30
    )
    
    if response.status_code != 200:
        print(f"❌ DB 조회 실패: {response.status_code}")
        return
    
    images = response.json()
    total = len(images)
    
    if total == 0:
        print("✅ 분류할 이미지가 없습니다!")
        return
    
    print(f"📋 분류 대상: {total}개 이미지\n")
    
    stats = {'REAL_CASE': 0, 'NEWS': 0, 'NOISE': 0, 'failed': 0}
    
    for idx, image in enumerate(images, 1):
        image_id = image['id']
        text = image.get('translated_text') or image.get('ocr_text', '')
        
        if not text or len(text.strip()) < 10:
            print(f"[{idx}/{total}] ID {image_id}: ⏭️  텍스트 부족, NOISE로 분류")
            classification = 'NOISE'
        else:
            print(f"[{idx}/{total}] ID {image_id}: 분류 중...", end=' ')
            classification = classify_with_solar(text)
            print(f"✅ {classification}")
        
        # DB 업데이트
        update_response = requests.patch(
            f"{SUPABASE_URL}/rest/v1/phishing_images?id=eq.{image_id}",
            headers=headers,
            json={"classification": classification},
            timeout=10
        )
        
        if update_response.status_code in [200, 204]:
            stats[classification] += 1
        else:
            print(f"      ⚠️  DB 업데이트 실패")
            stats['failed'] += 1
        
        time.sleep(0.5)  # Rate limiting
    
    # 결과
    print("\n" + "="*100)
    print("✅ 분류 완료!")
    print("="*100)
    print(f"   총 처리: {total}개")
    print(f"   REAL_CASE: {stats['REAL_CASE']}개")
    print(f"   NEWS: {stats['NEWS']}개")
    print(f"   NOISE: {stats['NOISE']}개")
    print(f"   실패: {stats['failed']}개")
    print("="*100 + "\n")

if __name__ == "__main__":
    classify_images()
