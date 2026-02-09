#!/usr/bin/env python3
"""
glm-ocr 프롬프트 개선 후 재테스트
공식 사용법: "Text Recognition: " 형식
"""
import os
import requests
import json
import base64
from dotenv import load_dotenv

load_dotenv()

OPENAI_KEY = os.getenv('OPENAI_API_KEY')

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def ocr_with_glm_improved(image_path):
    """개선된 glm-ocr 프롬프트"""
    try:
        base64_image = encode_image(image_path)
        
        # glm-ocr 공식 사용법: "Text Recognition: "
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "glm-ocr",
                "prompt": "Text Recognition (Korean and English only, output in original language):",
                "images": [base64_image],
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 2000
                }
            },
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()['response'].strip()
        return f"[Error: {response.status_code}]"
    except Exception as e:
        return f"[Error: {str(e)[:100]}]"

def ocr_with_openai(image_path):
    """OpenAI Vision"""
    try:
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
                        {"type": "text", "text": "이 이미지에서 보이는 모든 텍스트를 정확하게 추출해주세요. 한글과 영어를 원본 언어 그대로 추출하고, 설명 없이 텍스트만 출력하세요."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }],
                "max_tokens": 1024,
                "temperature": 0.1
            },
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content'].strip()
        return f"[Error: {response.status_code}]"
    except Exception as e:
        return f"[Error: {str(e)[:100]}]"

# 테스트할 이미지
test_images = [
    ("data/images/phishing/스미싱_문자_사례_2.jpg", "🇰🇷 한국어 스미싱 문자"),
    ("data/images/phishing/스미싱_문자_사례_3.jpg", "🇰🇷 미끼문자 사기수법"),
    ("data/images/phishing/스미싱_문자_사례_9.jpg", "🇰🇷 롯데리아 쿠폰 사칭"),
]

print("\n" + "="*100)
print("🔍 glm-ocr 프롬프트 개선 후 재테스트")
print("="*100 + "\n")

for img_path, img_desc in test_images:
    if not os.path.exists(img_path):
        print(f"⚠️ 파일 없음: {img_path}\n")
        continue
    
    print(f"\n{'='*100}")
    print(f"📸 {img_desc}")
    print(f"파일: {img_path}")
    print(f"{'='*100}\n")
    
    # glm-ocr (개선된 프롬프트)
    print("🔷 glm-ocr (개선된 프롬프트):")
    print("-" * 100)
    result = ocr_with_glm_improved(img_path)
    if len(result) > 500:
        print(result[:500] + f"\n... (총 {len(result)}자)")
    else:
        print(result)
    print()
    
    # OpenAI Vision (비교용)
    print("🤖 OpenAI Vision (비교):")
    print("-" * 100)
    result = ocr_with_openai(img_path)
    if len(result) > 500:
        print(result[:500] + f"\n... (총 {len(result)}자)")
    else:
        print(result)
    print()

print("="*100)
print("✅ 완료!")
print("="*100)
