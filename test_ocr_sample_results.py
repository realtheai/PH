#!/usr/bin/env python3
"""
각 모델의 실제 OCR 추출 결과를 샘플로 보여주기
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

def ocr_with_model(image_path, model_name, model_type="ollama"):
    try:
        base64_image = encode_image(image_path)
        
        if model_type == "ollama":
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": model_name,
                    "prompt": "Extract all text from this image. Output only the extracted text in the original language. Do not add explanations.",
                    "images": [base64_image],
                    "stream": False,
                    "options": {"temperature": 0.1, "num_predict": 1000}
                },
                timeout=60
            )
            if response.status_code == 200:
                return response.json()['response'].strip()
        else:  # OpenAI
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
                            {"type": "text", "text": "이 이미지에서 보이는 모든 텍스트를 정확하게 추출해주세요. 텍스트만 출력하세요."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]
                    }],
                    "max_tokens": 1024,
                    "temperature": 0.2
                },
                timeout=60
            )
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content'].strip()
        
        return f"[Error: {response.status_code}]"
    except Exception as e:
        return f"[Error: {str(e)[:50]}]"

# 테스트할 이미지 (한국어 1개, 영문 1개)
test_images = [
    ("data/images/phishing/스미싱_문자_사례_2.jpg", "🇰🇷 한국어 스미싱 문자"),
    ("data/images/phishing/스미싱_문자_사례_9.jpg", "🇰🇷 롯데리아 쿠폰 사칭")
]

print("\n" + "="*100)
print("🔍 실제 OCR 추출 결과 비교")
print("="*100 + "\n")

for img_path, img_desc in test_images:
    if not os.path.exists(img_path):
        print(f"⚠️ 파일 없음: {img_path}\n")
        continue
    
    print(f"\n{'='*100}")
    print(f"📸 {img_desc}")
    print(f"파일: {img_path}")
    print(f"{'='*100}\n")
    
    # 각 모델 테스트
    models = [
        ("🔷 glm-ocr", "glm-ocr", "ollama"),
        ("🟦 qwen3-vl:8b", "qwen3-vl:8b", "ollama"),
        ("🟪 deepseek-ocr", "deepseek-ocr", "ollama"),
        ("🤖 OpenAI Vision", "gpt-4o-mini", "openai")
    ]
    
    for emoji_name, model, model_type in models:
        print(f"{emoji_name}:")
        print("-" * 100)
        
        result = ocr_with_model(img_path, model, model_type)
        
        if len(result) > 500:
            print(result[:500] + f"\n... (총 {len(result)}자)")
        else:
            print(result)
        
        print()

print("="*100)
print("✅ 완료!")
print("="*100)
