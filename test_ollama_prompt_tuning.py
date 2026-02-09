#!/usr/bin/env python3
"""
Ollama 프롬프트 최적화 벤치마크
"""
import requests
import json
import time
import numpy as np
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_KEY = os.getenv('OPENAI_API_KEY')

test_samples = [
    {"text": "택배가 도착했습니다. 주소지 변경: http://bit.ly/abc", "expected": "REAL_CASE"},
    {"text": "안녕 아들이야. 급하게 돈 필요해. 카톡 안돼서 문자해", "expected": "REAL_CASE"},
    {"text": "경찰청, 보이스피싱 예방 캠페인 실시", "expected": "NEWS"},
    {"text": "[Web] 국민연금 환급금 조회하세요", "expected": "REAL_CASE"},
    {"text": "오늘 날씨가 좋네요", "expected": "NOISE"},
]

# Ollama 최적화 프롬프트
OLLAMA_PROMPT = """You are a phishing classification expert.

Classify this Korean text into ONE category:
- REAL_CASE: actual phishing/smishing message
- NEWS: news article about phishing  
- NOISE: unrelated content

Text: {text}

Answer in JSON format ONLY:
{{"classification": "REAL_CASE"}}
or
{{"classification": "NEWS"}}
or
{{"classification": "NOISE"}}

Your answer:"""

print("\n" + "="*60)
print("🔬 Ollama 프롬프트 최적화 테스트")
print("="*60 + "\n")

results = []

for i, sample in enumerate(test_samples, 1):
    text = sample['text']
    expected = sample['expected']
    
    print(f"[{i}/{len(test_samples)}] {text[:30]}...")
    print(f"   정답: {expected}")
    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3:8b",
                "prompt": OLLAMA_PROMPT.format(text=text),
                "stream": False,
                "options": {
                    "temperature": 0.0,  # 더 결정적으로
                    "num_predict": 50,    # 짧게
                    "stop": ["\n", "Note"]  # 불필요한 설명 차단
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            content = response.json()['response'].strip()
            print(f"   원본 응답: {content[:80]}")
            
            # JSON 파싱
            try:
                result = json.loads(content)['classification']
            except:
                # Fallback: 텍스트에서 추출
                if 'REAL_CASE' in content.upper():
                    result = 'REAL_CASE'
                elif 'NEWS' in content.upper():
                    result = 'NEWS'
                elif 'NOISE' in content.upper():
                    result = 'NOISE'
                else:
                    result = 'ERROR'
            
            correct = '✅' if result == expected else '❌'
            print(f"   결과: {result} {correct}")
            results.append(result == expected)
    except Exception as e:
        print(f"   ERROR: {str(e)[:50]}")
        results.append(False)
    
    print()
    time.sleep(0.2)

accuracy = (sum(results) / len(results)) * 100
print(f"\n📊 Ollama 정확도: {accuracy:.0f}% ({sum(results)}/{len(results)})\n")

if accuracy >= 80:
    print("✅ 프롬프트 최적화 성공! 사용 가능합니다.")
else:
    print("⚠️  추가 프롬프트 튜닝 필요하거나, 다른 모델(Qwen2) 시도 권장")

print("\n💡 권장사항:")
print("   1. Qwen2:7b 다운로드: ollama pull qwen2:7b")
print("   2. 한국어 특화 모델로 재테스트")
print()
