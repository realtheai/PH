#!/usr/bin/env python3
"""
번역 모델 비교: OpenAI vs Solar
- 영어 → 한국어 번역 품질
- 속도 비교
"""
import requests
import json
import time
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_KEY = os.getenv('OPENAI_API_KEY')

# 실제 해외 피싱 뉴스 샘플
test_samples = [
    {
        "original": "Warning: New phishing scam targets bank customers with fake SMS messages claiming unauthorized transactions.",
        "context": "뉴스 기사"
    },
    {
        "original": "Hi mom, my phone broke. Can you send me money urgently? I'll pay you back tomorrow.",
        "context": "가족 사칭"
    },
    {
        "original": "Your Amazon package has been delayed. Please update your shipping address here: bit.ly/update",
        "context": "택배 사칭"
    },
    {
        "original": "IRS Notice: You have unclaimed tax refund. Click here to claim within 24 hours.",
        "context": "기관 사칭"
    },
    {
        "original": "Police report reveals cryptocurrency phishing attacks increased 300% in 2024.",
        "context": "뉴스 기사"
    }
]

SOLAR_PROMPT = """다음 영어 텍스트를 자연스러운 한국어로 번역하세요.

피싱/스미싱 관련 내용이므로:
- 전문 용어는 정확하게 번역
- 맥락을 고려하여 자연스럽게
- 원문의 의미를 정확히 전달

영어 원문: {text}

한국어 번역만 출력하세요:"""

OPENAI_PROMPT = """다음 영어 텍스트를 자연스러운 한국어로 번역하세요.

피싱/스미싱 관련 내용이므로 전문 용어를 정확히 번역하고, 맥락을 고려하세요.

영어: {text}

한국어:"""

print("\n" + "="*80)
print("🌐 번역 모델 비교: OpenAI vs Solar 10.7B")
print("="*80 + "\n")

solar_times = []
openai_times = []

for i, sample in enumerate(test_samples, 1):
    original = sample['original']
    context = sample['context']
    
    print(f"[{i}/{len(test_samples)}] {context}")
    print(f"   원문: {original}")
    print()
    
    # Solar 번역
    try:
        start = time.time()
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "solar:10.7b",
                "prompt": SOLAR_PROMPT.format(text=original),
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 200
                }
            },
            timeout=60
        )
        solar_time = time.time() - start
        
        if response.status_code == 200:
            solar_result = response.json()['response'].strip()
            solar_times.append(solar_time)
            print(f"   Solar: {solar_result}")
            print(f"   시간: {solar_time:.2f}s")
    except Exception as e:
        print(f"   Solar ERROR: {str(e)[:50]}")
    
    print()
    
    # OpenAI 번역
    try:
        start = time.time()
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={'Authorization': f'Bearer {OPENAI_KEY}', 'Content-Type': 'application/json'},
            json={
                'model': 'gpt-4o-mini',
                'messages': [
                    {'role': 'system', 'content': '전문 번역가'},
                    {'role': 'user', 'content': OPENAI_PROMPT.format(text=original)}
                ],
                'temperature': 0.3
            },
            timeout=30
        )
        openai_time = time.time() - start
        
        if response.status_code == 200:
            openai_result = response.json()['choices'][0]['message']['content']
            openai_times.append(openai_time)
            print(f"   OpenAI: {openai_result}")
            print(f"   시간: {openai_time:.2f}s")
    except Exception as e:
        print(f"   OpenAI ERROR")
    
    print()
    print("-" * 80)
    print()
    time.sleep(0.3)

# 최종 평가
print("="*80)
print("📊 번역 품질 비교 결과")
print("="*80 + "\n")

solar_avg = np.mean(solar_times) if solar_times else 0
openai_avg = np.mean(openai_times) if openai_times else 0

print(f"⚡ 속도:")
print(f"   Solar:  {solar_avg:.2f}s/건")
print(f"   OpenAI: {openai_avg:.2f}s/건")

if solar_avg < openai_avg:
    print(f"   → Solar가 {openai_avg/solar_avg:.1f}배 빠름! ✅")
else:
    print(f"   → OpenAI가 {solar_avg/openai_avg:.1f}배 빠름")

print()

print("="*80)
print("💡 번역 품질 평가")
print("="*80)
print("""
위 번역 결과를 직접 확인해보세요:

✅ 확인 포인트:
1. 자연스러움: 한국어 표현이 어색하지 않은가?
2. 정확성: 원문의 의미를 정확히 전달했는가?
3. 전문용어: "phishing" → "피싱", "scam" → "사기" 등 정확한가?
4. 맥락 이해: 피싱 관련 맥락을 이해하고 번역했는가?

💡 주관적 평가가 필요합니다!
""")

print()
print("="*80)
print("🚀 실전 적용 권장 사항")
print("="*80)
print(f"""
📊 현재까지 테스트 결과:

| 작업 | OpenAI | Solar | Ollama BGE-M3 | 추천 |
|------|--------|-------|---------------|------|
| 분류 | 90% | **90%** | - | ✅ Solar |
| 임베딩 | 75% | - | **87.5%** | ✅ BGE-M3 |
| 번역 | {openai_avg:.2f}s | **{solar_avg:.2f}s** | - | 품질 확인 필요 |

💰 비용 절감 (Solar + BGE-M3):
   - 초기 처리: ~$0.64 절약
   - 일일 크롤링: ~$0.05/일 → $18/년 절약

🎯 추천 전략:
1. 분류: Solar 10.7B
2. 임베딩: BGE-M3
3. 번역: 품질 확인 후 결정
   - Solar 품질 OK → Solar
   - Solar 품질 부족 → OpenAI (번역은 비용 낮음)
""")

print("\n✅ 번역 테스트 완료!")
print("\n💬 Solar 번역 품질이 만족스러우신가요?\n")
