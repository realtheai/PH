#!/usr/bin/env python3
"""
성공한 이미지(ID 690)로 모델 비교 테스트
"""
import os
import requests
import base64
import time
from dotenv import load_dotenv

load_dotenv()

OPENAI_KEY = os.getenv('OPENAI_API_KEY')

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def test_glm_ocr(image_path):
    """glm-ocr 테스트 (공식 프롬프트 사용)"""
    try:
        start = time.time()
        base64_image = encode_image(image_path)
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "glm-ocr",
                "prompt": "Text Recognition:",
                "images": [base64_image],
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 2000
                }
            },
            timeout=120
        )
        
        elapsed = time.time() - start
        
        if response.status_code == 200:
            text = response.json()['response'].strip()
            return {'success': True, 'text': text, 'time': elapsed}
        return {'success': False, 'error': f"Status {response.status_code}", 'time': elapsed}
    except Exception as e:
        return {'success': False, 'error': str(e), 'time': 0}

def test_deepseek_ocr(image_path):
    """deepseek-ocr 테스트"""
    try:
        start = time.time()
        base64_image = encode_image(image_path)
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "deepseek-ocr",
                "prompt": "Extract all text from this image in original language (Korean or English):",
                "images": [base64_image],
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 2000
                }
            },
            timeout=120
        )
        
        elapsed = time.time() - start
        
        if response.status_code == 200:
            text = response.json()['response'].strip()
            return {'success': True, 'text': text, 'time': elapsed}
        return {'success': False, 'error': f"Status {response.status_code}", 'time': elapsed}
    except Exception as e:
        return {'success': False, 'error': str(e), 'time': 0}

def test_openai_vision(image_path):
    """OpenAI Vision 테스트 (기존 성공한 방식)"""
    try:
        start = time.time()
        base64_image = encode_image(image_path)
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENAI_KEY}"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """이 이미지에서 보이는 모든 텍스트를 정확하게 추출해주세요.

출력 형식:
- 한글과 영어를 모두 정확히 추출
- 줄바꿈 유지
- 특수문자 포함
- 광고/배너 제외

텍스트:"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        }
                    ]
                }],
                "max_tokens": 1024,
                "temperature": 0.2
            },
            timeout=60
        )
        
        elapsed = time.time() - start
        
        if response.status_code == 200:
            text = response.json()['choices'][0]['message']['content'].strip()
            return {'success': True, 'text': text, 'time': elapsed}
        return {'success': False, 'error': f"Status {response.status_code}", 'time': elapsed}
    except Exception as e:
        return {'success': False, 'error': str(e), 'time': 0}

# 테스트할 이미지들
test_images = [
    ("data/images/phishing/결제_알림_피싱_문자_17.jpg", "✅ OpenAI 성공 케이스 (ID 690)"),
    ("data/images/phishing/스미싱_문자_사례_9.jpg", "🇰🇷 롯데리아 쿠폰"),
    ("data/images/phishing/스미싱_문자_사례_2.jpg", "🇰🇷 스미싱 문자"),
]

print("\n" + "="*100)
print("🔍 OCR 모델 비교 - 성공 케이스 포함")
print("="*100 + "\n")

for img_path, desc in test_images:
    if not os.path.exists(img_path):
        print(f"⚠️ 파일 없음: {img_path}\n")
        continue
    
    print(f"\n{'='*100}")
    print(f"📸 {desc}")
    print(f"파일: {img_path}")
    print(f"{'='*100}\n")
    
    # 각 모델 테스트
    models = [
        ("🔷 glm-ocr", test_glm_ocr),
        ("🟪 deepseek-ocr", test_deepseek_ocr),
        ("🤖 OpenAI Vision", test_openai_vision)
    ]
    
    for model_name, test_func in models:
        print(f"{model_name}:")
        print("-" * 100)
        
        result = test_func(img_path)
        
        if result['success']:
            text = result['text']
            print(f"⏱️  시간: {result['time']:.2f}초")
            print(f"📝 길이: {len(text)}자")
            print(f"내용:")
            if len(text) > 400:
                print(text[:400] + f"\n... (이하 생략, 총 {len(text)}자)")
            else:
                print(text)
        else:
            print(f"❌ 실패: {result.get('error')}")
        
        print()

print("="*100)
print("✅ 완료!")
print("="*100)
