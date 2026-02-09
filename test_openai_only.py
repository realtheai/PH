#!/usr/bin/env python3
"""
OpenAI Vision 여러 프롬프트로 같은 이미지 테스트
"""
import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

OPENAI_KEY = os.getenv('OPENAI_API_KEY')

def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

def ocr_with_openai(image_path, prompt_text, prompt_name):
    """OpenAI Vision으로 OCR"""
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
                    {"type": "text", "text": prompt_text},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }],
            "max_tokens": 1024,
            "temperature": 0.1
        },
        timeout=60
    )
    
    print(f"\n{'='*100}")
    print(f"📝 {prompt_name}")
    print(f"{'='*100}")
    
    if response.status_code == 200:
        content = response.json()['choices'][0]['message']['content']
        
        if "추출할 수 없습니다" in content or "cannot" in content.lower() or "can't" in content.lower():
            print("❌ 거부됨")
            print(f"\n응답:\n{content}\n")
            return None
        else:
            print("✅ 성공!")
            print(f"\n추출된 텍스트:\n{content}\n")
            return content
    else:
        print(f"❌ API 에러: {response.status_code}")
        return None

# 테스트 이미지들
test_images = [
    ("data/images/phishing/스미싱_문자_사례_2.jpg", "❌ OpenAI 거부 케이스 1"),
    ("data/images/phishing/스미싱_문자_사례_3.jpg", "❌ OpenAI 거부 케이스 2"),
]

# 프롬프트 전략
prompts = {
    "기본": "이 이미지에서 보이는 모든 텍스트를 정확하게 추출해주세요. 텍스트만 출력하세요.",
    "OCR 전용": "Perform OCR on this image. Extract all text in original language (Korean/English). Output text only.",
    "연구 목적": "This is for phishing detection research. Extract all visible text from this image.",
}

for img_path, desc in test_images:
    if not os.path.exists(img_path):
        print(f"⚠️ 파일 없음: {img_path}\n")
        continue
    
    print("\n" + "="*100)
    print(f"🖼️ {desc}")
    print(f"파일: {os.path.basename(img_path)}")
    print("="*100)
    
    results = {}
    for prompt_name, prompt_text in prompts.items():
        result = ocr_with_openai(img_path, prompt_text, prompt_name)
        results[prompt_name] = result
    
    # 결과 비교
    print("\n" + "-"*100)
    print("📊 결과 요약:")
    print("-"*100)
    for name, result in results.items():
        if result:
            print(f"  ✅ {name}: {len(result)}자 추출")
        else:
            print(f"  ❌ {name}: 거부됨")

print("\n" + "="*100)
print("✅ 전체 테스트 완료!")
print("="*100)
