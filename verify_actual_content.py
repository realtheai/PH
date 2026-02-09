#!/usr/bin/env python3
"""
실제 이미지 내용 확인 - Ollama vs OpenAI 비교
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

def ocr_with_ollama(image_path):
    """Ollama glm-ocr로 OCR"""
    base64_image = encode_image(image_path)
    
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "glm-ocr",
            "prompt": "Text Recognition (Korean and English only, output in original language):",
            "images": [base64_image],
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": 2000}
        },
        timeout=60
    )
    
    if response.status_code == 200:
        return response.json().get('response', '').strip()
    return f"Error: {response.status_code}"

def ocr_with_openai(image_path, prompt_text):
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
    
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    return f"Error: {response.status_code}"

# 테스트 이미지
test_image = "data/images/phishing/스미싱_문자_사례_2.jpg"

print("\n" + "="*100)
print("🔍 실제 이미지 내용 확인")
print(f"이미지: {os.path.basename(test_image)}")
print("="*100)

# Ollama 결과
print("\n" + "-"*100)
print("📌 Ollama glm-ocr 결과:")
print("-"*100)
ollama_result = ocr_with_ollama(test_image)
print(ollama_result)

# OpenAI 결과 (성공한 프롬프트)
print("\n" + "-"*100)
print("📌 OpenAI Vision 결과 (기존 프롬프트):")
print("-"*100)
openai_result1 = ocr_with_openai(
    test_image,
    "이 이미지에서 보이는 모든 텍스트를 정확하게 추출해주세요. 한글과 영어를 모두 정확히 추출하고, 줄바꿈을 유지하세요. 텍스트만 출력하고 설명은 추가하지 마세요."
)
print(openai_result1)

# OpenAI 결과 2 (연구목적 프롬프트)
print("\n" + "-"*100)
print("📌 OpenAI Vision 결과 (연구목적 프롬프트):")
print("-"*100)
openai_result2 = ocr_with_openai(
    test_image,
    "This is a research image for phishing detection analysis. Please extract all visible text from this image for academic research purposes. Include Korean and English text. Output only the extracted text."
)
print(openai_result2)

print("\n" + "="*100)
print("✅ 비교 완료!")
print("="*100)
