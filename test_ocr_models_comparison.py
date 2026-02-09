#!/usr/bin/env python3
"""
4개 OCR 모델 비교 테스트:
- glm-ocr (Ollama)
- qwen3-vl:8b (Ollama)
- deepseek-ocr (Ollama)
- OpenAI Vision (gpt-4o-mini)

테스트: 영문 이미지 10개 + 한국어 이미지 10개 = 총 20개
"""
import os
import requests
import json
import time
import base64
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

OPENAI_KEY = os.getenv('OPENAI_API_KEY')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

db_headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

def encode_image(image_path):
    """이미지를 base64로 인코딩"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def ocr_with_ollama(image_path, model_name):
    """Ollama 모델로 OCR"""
    try:
        start = time.time()
        base64_image = encode_image(image_path)
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model_name,
                "prompt": "Extract all text from this image. Output only the extracted text in the original language (Korean or English). Do not add any explanations.",
                "images": [base64_image],
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 1000
                }
            },
            timeout=180
        )
        
        elapsed = time.time() - start
        
        if response.status_code == 200:
            result = response.json()
            text = result.get('response', '').strip()
            return {
                'success': True,
                'text': text,
                'time': elapsed,
                'length': len(text)
            }
        else:
            return {
                'success': False,
                'error': f"Status {response.status_code}",
                'time': elapsed
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'time': 0
        }

def ocr_with_openai(image_path):
    """OpenAI Vision으로 OCR"""
    try:
        start = time.time()
        base64_image = encode_image(image_path)
        
        url = "https://api.openai.com/v1/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_KEY}"
        }
        
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "이 이미지에서 보이는 모든 텍스트를 정확하게 추출해주세요. 한글과 영어를 모두 정확히 추출하고, 줄바꿈을 유지하세요. 텍스트만 출력하고 설명은 추가하지 마세요."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 1024,
            "temperature": 0.2
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            result = response.json()
            text = result['choices'][0]['message']['content'].strip()
            return {
                'success': True,
                'text': text,
                'time': elapsed,
                'length': len(text)
            }
        else:
            return {
                'success': False,
                'error': f"Status {response.status_code}",
                'time': elapsed
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'time': 0
        }

def is_korean_image(query):
    """이미지가 한국어 관련인지 판단"""
    korean_keywords = ['스미싱', '피싱', '문자', '사례', '한국']
    return any(keyword in query for keyword in korean_keywords)

def main():
    print("\n" + "="*100)
    print("🔍 OCR 모델 비교 테스트 (4개 모델 × 20개 이미지)")
    print("="*100 + "\n")
    
    # 1. 이미지 가져오기
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/phishing_images",
        headers=db_headers,
        params={'select': 'id,local_path,query,source', 'limit': 100}
    )
    
    if response.status_code != 200:
        print(f"❌ 이미지 조회 실패: {response.status_code}")
        return
    
    all_images = response.json()
    
    # 한국어 이미지와 영문 이미지 분류
    korean_images = [img for img in all_images if img.get('query') and is_korean_image(img['query'])][:10]
    english_images = [img for img in all_images if img not in korean_images][:10]
    
    test_images = korean_images + english_images
    
    print(f"📸 테스트 이미지:")
    print(f"   한국어 이미지: {len(korean_images)}개")
    print(f"   영문 이미지: {len(english_images)}개")
    print(f"   총: {len(test_images)}개\n")
    
    # 통계
    stats = {
        'glm-ocr': {'success': 0, 'failed': 0, 'total_time': 0, 'total_length': 0, 'results': []},
        'qwen3-vl': {'success': 0, 'failed': 0, 'total_time': 0, 'total_length': 0, 'results': []},
        'deepseek-ocr': {'success': 0, 'failed': 0, 'total_time': 0, 'total_length': 0, 'results': []},
        'openai': {'success': 0, 'failed': 0, 'total_time': 0, 'total_length': 0, 'results': []}
    }
    
    models = [
        ('glm-ocr', 'glm-ocr', '🔷'),
        ('qwen3-vl', 'qwen3-vl:8b', '🟦'),
        ('deepseek-ocr', 'deepseek-ocr', '🟪'),
        ('openai', 'OpenAI Vision', '🤖')
    ]
    
    for i, img in enumerate(test_images, 1):
        img_id = img['id']
        img_path = img['local_path']
        img_type = "🇰🇷 한국어" if img in korean_images else "🇺🇸 영문"
        
        print(f"[{i}/{len(test_images)}] {img_type} - ID: {img_id}")
        print(f"   파일: {img_path}")
        
        # 파일 존재 확인
        if not os.path.exists(img_path):
            print(f"   ⚠️ 파일 없음\n")
            continue
        
        # 각 모델 테스트
        for stat_key, model_name, emoji in models:
            print(f"   {emoji} {model_name} 테스트 중...", end=' ', flush=True)
            
            if stat_key == 'openai':
                result = ocr_with_openai(img_path)
            else:
                result = ocr_with_ollama(img_path, model_name)
            
            if result['success']:
                stats[stat_key]['success'] += 1
                stats[stat_key]['total_time'] += result['time']
                stats[stat_key]['total_length'] += result['length']
                stats[stat_key]['results'].append(result)
                print(f"✅ ({result['time']:.1f}s, {result['length']}자)")
            else:
                stats[stat_key]['failed'] += 1
                print(f"❌ {result.get('error', 'Unknown')}")
        
        print()
        time.sleep(0.5)
    
    # 최종 통계
    print("\n" + "="*100)
    print("📊 최종 비교 결과")
    print("="*100 + "\n")
    
    print(f"{'모델':<20} {'성공':<10} {'실패':<10} {'평균 속도':<15} {'평균 길이':<15}")
    print("-" * 100)
    
    for stat_key, model_display, emoji in models:
        stat = stats[stat_key]
        success_rate = (stat['success'] / len(test_images) * 100) if len(test_images) > 0 else 0
        avg_time = (stat['total_time'] / stat['success']) if stat['success'] > 0 else 0
        avg_length = (stat['total_length'] / stat['success']) if stat['success'] > 0 else 0
        
        print(f"{emoji} {model_display:<17} {stat['success']}/{len(test_images):<7} {stat['failed']:<10} {avg_time:.2f}초<13 {avg_length:.0f}자<13")
    
    print("\n" + "="*100)
    
    # 속도 비교
    print("\n⚡ 속도 순위:")
    speed_ranking = []
    for stat_key, model_display, emoji in models:
        stat = stats[stat_key]
        if stat['success'] > 0:
            avg_time = stat['total_time'] / stat['success']
            speed_ranking.append((emoji + " " + model_display, avg_time))
    
    speed_ranking.sort(key=lambda x: x[1])
    for i, (model, avg_time) in enumerate(speed_ranking, 1):
        print(f"   {i}. {model}: {avg_time:.2f}초/건")
    
    # 텍스트 추출량 비교
    print("\n📝 텍스트 추출량 순위:")
    length_ranking = []
    for stat_key, model_display, emoji in models:
        stat = stats[stat_key]
        if stat['success'] > 0:
            avg_length = stat['total_length'] / stat['success']
            length_ranking.append((emoji + " " + model_display, avg_length))
    
    length_ranking.sort(key=lambda x: x[1], reverse=True)
    for i, (model, length) in enumerate(length_ranking, 1):
        print(f"   {i}. {model}: {length:.0f}자/건")
    
    print("\n" + "="*100)
    print("✅ 테스트 완료!")
    print("="*100 + "\n")

if __name__ == "__main__":
    main()
