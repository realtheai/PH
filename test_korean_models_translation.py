#!/usr/bin/env python3
"""
한국어 특화 모델 번역 비교 테스트
- timHan/llama3korean8B4QKM:latest (Llama3 Korean)
- seungduk-yanolja/EEVE-Korean-Instruct-7B-v2.0-Preview:latest (EEVE)
- OpenAI gpt-4o-mini (기준)
"""
import requests
import json
import time
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_KEY = os.getenv('OPENAI_API_KEY')

# 실제 해외 피싱 뉴스/메시지 샘플
test_samples = [
    {
        "original": "Warning: New phishing scam targets bank customers with fake SMS messages claiming unauthorized transactions.",
        "context": "뉴스 기사",
        "expected_keywords": ["경고", "피싱", "사기", "은행", "고객", "무단", "거래"]
    },
    {
        "original": "Hi mom, my phone broke. Can you send me money urgently? I'll pay you back tomorrow.",
        "context": "가족 사칭",
        "expected_keywords": ["엄마", "전화", "고장", "돈", "급히", "갚다"]
    },
    {
        "original": "Your Amazon package has been delayed. Please update your shipping address here: bit.ly/update",
        "context": "택배 사칭",
        "expected_keywords": ["아마존", "패키지", "지연", "배송", "주소", "업데이트"]
    },
    {
        "original": "IRS Notice: You have unclaimed tax refund. Click here to claim within 24 hours.",
        "context": "기관 사칭",
        "expected_keywords": ["국세청", "세금", "환급", "24시간"]
    },
    {
        "original": "Police report reveals cryptocurrency phishing attacks increased 300% in 2024.",
        "context": "뉴스 기사",
        "expected_keywords": ["경찰", "보고서", "암호화폐", "피싱", "공격", "증가", "300%", "2024"]
    }
]

LLAMA3_KOREAN_PROMPT = """다음 영어 텍스트를 자연스러운 한국어로 번역하세요.

피싱/스미싱 관련 내용입니다. 전문 용어를 정확히 번역하고, 자연스러운 한국어로 표현하세요.

영어: {text}

한국어 번역:"""

EEVE_PROMPT = """다음 영어 텍스트를 자연스러운 한국어로 번역하세요.

영어: {text}

한국어:"""

OPENAI_PROMPT = """다음 영어 텍스트를 자연스러운 한국어로 번역하세요.

피싱/스미싱 관련 내용이므로 전문 용어를 정확히 번역하고, 맥락을 고려하세요.

영어: {text}

한국어:"""

def translate_with_ollama(model, prompt, text):
    """Ollama 모델로 번역"""
    try:
        start = time.time()
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt.format(text=text),
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 300
                }
            },
            timeout=90
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            result = response.json()['response'].strip()
            # 불필요한 주석 제거
            if '(' in result and ')' in result:
                result = result.split('(')[0].strip()
            if '※' in result:
                result = result.split('※')[0].strip()
            return result, elapsed
        else:
            return f"ERROR: {response.status_code}", elapsed
    except Exception as e:
        return f"ERROR: {str(e)[:50]}", 0

def translate_with_openai(text):
    """OpenAI로 번역"""
    try:
        start = time.time()
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={'Authorization': f'Bearer {OPENAI_KEY}', 'Content-Type': 'application/json'},
            json={
                'model': 'gpt-4o-mini',
                'messages': [
                    {'role': 'system', 'content': '전문 번역가'},
                    {'role': 'user', 'content': OPENAI_PROMPT.format(text=text)}
                ],
                'temperature': 0.3
            },
            timeout=30
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            result = response.json()['choices'][0]['message']['content']
            return result, elapsed
        else:
            return f"ERROR: {response.status_code}", elapsed
    except Exception as e:
        return f"ERROR", elapsed

print("\n" + "="*100)
print("🇰🇷 한국어 특화 모델 번역 성능 비교")
print("="*100 + "\n")

results = {
    'llama3korean': {'times': [], 'scores': []},
    'eeve': {'times': [], 'scores': []},
    'openai': {'times': [], 'scores': []}
}

for i, sample in enumerate(test_samples, 1):
    original = sample['original']
    context = sample['context']
    keywords = sample['expected_keywords']
    
    print(f"[{i}/{len(test_samples)}] {context}")
    print(f"원문: {original}")
    print()
    
    # Llama3 Korean
    print("1️⃣ Llama3-Korean-8B")
    llama3_result, llama3_time = translate_with_ollama(
        "timHan/llama3korean8B4QKM:latest",
        LLAMA3_KOREAN_PROMPT,
        original
    )
    print(f"   {llama3_result}")
    print(f"   ⏱️ {llama3_time:.2f}s")
    results['llama3korean']['times'].append(llama3_time)
    
    # 키워드 매칭 스코어
    score = sum(1 for kw in keywords if kw in llama3_result) / len(keywords) * 100
    results['llama3korean']['scores'].append(score)
    print(f"   📊 키워드 매칭: {score:.0f}%")
    print()
    
    # EEVE Korean
    print("2️⃣ EEVE-Korean-7B")
    eeve_result, eeve_time = translate_with_ollama(
        "seungduk-yanolja/EEVE-Korean-Instruct-7B-v2.0-Preview:latest",
        EEVE_PROMPT,
        original
    )
    print(f"   {eeve_result}")
    print(f"   ⏱️ {eeve_time:.2f}s")
    results['eeve']['times'].append(eeve_time)
    
    score = sum(1 for kw in keywords if kw in eeve_result) / len(keywords) * 100
    results['eeve']['scores'].append(score)
    print(f"   📊 키워드 매칭: {score:.0f}%")
    print()
    
    # OpenAI
    print("3️⃣ OpenAI GPT-4o-mini (기준)")
    openai_result, openai_time = translate_with_openai(original)
    print(f"   {openai_result}")
    print(f"   ⏱️ {openai_time:.2f}s")
    results['openai']['times'].append(openai_time)
    
    score = sum(1 for kw in keywords if kw in openai_result) / len(keywords) * 100
    results['openai']['scores'].append(score)
    print(f"   📊 키워드 매칭: {score:.0f}%")
    print()
    print("-" * 100)
    print()
    time.sleep(0.5)

# 최종 평가
print("="*100)
print("📊 번역 성능 종합 비교")
print("="*100 + "\n")

llama3_avg_time = sum(results['llama3korean']['times']) / len(results['llama3korean']['times'])
eeve_avg_time = sum(results['eeve']['times']) / len(results['eeve']['times'])
openai_avg_time = sum(results['openai']['times']) / len(results['openai']['times'])

llama3_avg_score = sum(results['llama3korean']['scores']) / len(results['llama3korean']['scores'])
eeve_avg_score = sum(results['eeve']['scores']) / len(results['eeve']['scores'])
openai_avg_score = sum(results['openai']['scores']) / len(results['openai']['scores'])

print("⚡ 속도 비교:")
print(f"   Llama3-Korean-8B:  {llama3_avg_time:.2f}s/건")
print(f"   EEVE-Korean-7B:    {eeve_avg_time:.2f}s/건")
print(f"   OpenAI GPT-4o-mini: {openai_avg_time:.2f}s/건")
print()

fastest = min([
    ('Llama3-Korean', llama3_avg_time),
    ('EEVE-Korean', eeve_avg_time),
    ('OpenAI', openai_avg_time)
], key=lambda x: x[1])
print(f"   ✅ 가장 빠름: {fastest[0]} ({fastest[1]:.2f}s)")
print()

print("🎯 번역 품질 비교 (키워드 매칭):")
print(f"   Llama3-Korean-8B:  {llama3_avg_score:.1f}%")
print(f"   EEVE-Korean-7B:    {eeve_avg_score:.1f}%")
print(f"   OpenAI GPT-4o-mini: {openai_avg_score:.1f}%")
print()

best = max([
    ('Llama3-Korean', llama3_avg_score),
    ('EEVE-Korean', eeve_avg_score),
    ('OpenAI', openai_avg_score)
], key=lambda x: x[1])
print(f"   ✅ 가장 정확: {best[0]} ({best[1]:.1f}%)")
print()

print("="*100)
print("💡 종합 평가")
print("="*100)
print("""
📝 평가 기준:
1. 키워드 매칭: 주요 용어가 정확히 번역되었는지
2. 자연스러움: 위 번역 결과를 직접 확인 필요
3. 속도: API 호출 시간

✅ 좋은 번역:
- 전문 용어 정확 (phishing → 피싱, scam → 사기)
- 자연스러운 한국어 (띄어쓰기, 문법)
- 맥락 이해 (은행 → Bank ❌, 은행 ✅)

❌ 나쁜 번역:
- 영어 섞임 (Bank, SMS, delay 등)
- 띄어쓰기 없음
- 오타/이상한 표현
""")

print()
print("="*100)
print("🚀 실전 적용 권장 사항")
print("="*100)
print(f"""
| 작업 | 현재 추천 | 대안 | 이유 |
|------|----------|------|------|
| 분류 | Solar 10.7B | - | 정확도 90%, 무료 |
| 임베딩 | BGE-M3 | - | RAG 87.5%, 무료 |
| 번역 | OpenAI | Llama3/EEVE? | 품질 확인 필요 |

💰 한국어 모델 사용 시 예상 비용 절감:
   - 번역도 로컬화 → 추가 $0.10/년 절약
   - 총 절감: ~$18/년

🎯 최종 결정을 위한 체크리스트:
1. 위 번역 결과가 모두 자연스러운가?
2. 전문 용어가 정확히 번역되었는가?
3. 실제 서비스에 사용해도 문제없는 품질인가?

💬 어떤 모델이 가장 마음에 드시나요?
""")

print("\n✅ 번역 테스트 완료!\n")
