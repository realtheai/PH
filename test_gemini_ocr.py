#!/usr/bin/env python3
"""
Gemini Vision API로 OCR 테스트
"""
import os
import requests
import base64
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

GEMINI_KEY = os.getenv('GEMINI_API_KEY')

def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

def ocr_with_gemini(image_path):
    """Gemini Vision으로 OCR"""
    try:
        base64_image = encode_image(image_path)
        
        # Gemini API 엔드포인트
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
        
        payload = {
            "contents": [{
                "parts": [
                    {"text": "Extract all visible text from this image. Output only the actual text content in the original language (Korean or English). Do not include any formatting tags, labels, or descriptions like [Text], [Web link], etc. Just output the text as it appears."},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": base64_image
                        }
                    }
                ]
            }],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 1024,
            }
        }
        
        response = requests.post(url, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            
            if 'candidates' in result and len(result['candidates']) > 0:
                content = result['candidates'][0]['content']['parts'][0]['text']
                return {'success': True, 'text': content.strip()}
            else:
                return {'success': False, 'error': 'No candidates'}
        else:
            return {'success': False, 'error': f"API Error: {response.status_code}", 'details': response.text[:200]}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}

# OpenAI가 실패한 이미지들로 테스트
test_images = [
    ("data/images/phishing/스미싱_문자_사례_4.jpg", "❌ OpenAI 거부"),
    ("data/images/phishing/스미싱_문자_사례_2.jpg", "✅ OpenAI 성공 (비교용)"),
]

print("\n" + "="*100)
print("🧪 Gemini Vision OCR 테스트")
print("="*100 + "\n")

for img_path, desc in test_images:
    if not os.path.exists(img_path):
        print(f"⚠️ 파일 없음: {img_path}\n")
        continue
    
    print(f"{'='*100}")
    print(f"📸 {desc}")
    print(f"파일: {os.path.basename(img_path)}")
    print(f"{'='*100}")
    
    result = ocr_with_gemini(img_path)
    
    if result['success']:
        text = result['text']
        print(f"✅ 성공: {len(text)}자 추출")
        print(f"\n추출된 텍스트:")
        print("-" * 100)
        print(text)
        print()
    else:
        print(f"❌ 실패: {result.get('error', 'Unknown')}")
        if 'details' in result:
            print(f"상세: {result['details']}")
        print()

print("="*100)
print("✅ 테스트 완료!")
print("="*100)
