#!/usr/bin/env python3
"""
OpenAI Vision API 응답 상세 분석
"""
import os
import requests
import base64
import json
from dotenv import load_dotenv

load_dotenv()

OPENAI_KEY = os.getenv('OPENAI_API_KEY')

def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

def test_openai_detailed(image_path, desc):
    """OpenAI Vision 상세 응답 확인"""
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
        
        print(f"\n{'='*100}")
        print(f"📸 {desc}")
        print(f"파일: {os.path.basename(image_path)}")
        print(f"{'='*100}")
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers:")
        for key, value in response.headers.items():
            if key.lower() in ['content-type', 'openai-processing-ms', 'x-ratelimit-remaining-tokens']:
                print(f"  {key}: {value}")
        print()
        
        if response.status_code == 200:
            result = response.json()
            
            # 전체 응답 구조 확인
            print("응답 구조:")
            print(f"  - choices: {len(result.get('choices', []))}개")
            
            if 'choices' in result and len(result['choices']) > 0:
                choice = result['choices'][0]
                message = choice.get('message', {})
                content = message.get('content', '')
                
                print(f"  - finish_reason: {choice.get('finish_reason')}")
                print(f"  - content 길이: {len(content)}자")
                print()
                print("추출된 텍스트:")
                print("-" * 100)
                print(content)
                print()
        else:
            print(f"❌ 에러:")
            print(response.text[:500])
            print()
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"\n❌ 예외 발생: {str(e)}\n")
        return False

# 테스트 실행
images_to_test = [
    ("data/images/phishing/결제_알림_피싱_문자_17.jpg", "✅ OpenAI 성공 케이스 (ID 690)"),
    ("data/images/phishing/스미싱_문자_사례_9.jpg", "🇰🇷 롯데리아 쿠폰 (부분 성공)"),
    ("data/images/phishing/스미싱_문자_사례_2.jpg", "❌ OpenAI 실패 케이스"),
]

print("\n" + "="*100)
print("🔍 OpenAI Vision API 상세 응답 분석")
print("="*100)

for img_path, desc in images_to_test:
    if os.path.exists(img_path):
        test_openai_detailed(img_path, desc)

print("\n" + "="*100)
print("✅ 분석 완료!")
print("="*100)
