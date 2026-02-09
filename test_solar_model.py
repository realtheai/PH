#!/usr/bin/env python3
"""
Solar 10.7B 모델 테스트 (한국 업스테이지 모델)
"""
import requests
import json
import time
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_KEY = os.getenv('OPENAI_API_KEY')

test_samples = [
    {"text": "택배가 도착했습니다. 주소지 변경을 원하시면 다음 링크를 클릭해주세요. http://bit.ly/abc123", "expected": "REAL_CASE"},
    {"text": "안녕하세요 아들이에요. 급하게 돈이 필요해서 연락드려요. 카톡 안되서 문자드려요.", "expected": "REAL_CASE"},
    {"text": "경찰청, 보이스피싱 예방 캠페인 실시. 작년 대비 피해액 20% 감소", "expected": "NEWS"},
    {"text": "[Web발신] 고객님의 국민연금 환급금이 있습니다. 다음 링크에서 조회하세요.", "expected": "REAL_CASE"},
    {"text": "오늘 날씨가 정말 좋네요. 산책하기 좋은 날씨입니다.", "expected": "NOISE"},
    {"text": "금융감독원을 사칭한 보이스피싱이 증가하고 있어 주의가 필요하다고 경찰청이 밝혔다.", "expected": "NEWS"},
    {"text": "안녕하세요 엄마예요. 핸드폰 고장나서 친구 폰으로 연락해요. 급한 일 있어요.", "expected": "REAL_CASE"},
    {"text": "삼성전자, 새로운 스마트폰 출시 예정", "expected": "NOISE"},
    {"text": "경찰관입니다. 귀하의 계좌가 범죄에 연루되었습니다. 즉시 연락주세요.", "expected": "REAL_CASE"},
    {"text": "부고 문자입니다. 고인의 명복을 빕니다. 부의금 계좌: 123-456-789", "expected": "REAL_CASE"}
]

PROMPT = """당신은 피싱/스미싱 분류 전문가입니다.

다음 텍스트를 분석하여 정확히 하나로 분류하세요:

- REAL_CASE: 실제 피싱/스미싱 메시지 (사기 목적의 문자/카톡)
- NEWS: 피싱 관련 뉴스 기사
- NOISE: 피싱과 무관한 일반 내용

텍스트: {text}

반드시 다음 JSON 형식으로만 답변하세요:
{{"classification": "REAL_CASE"}}
또는
{{"classification": "NEWS"}}
또는
{{"classification": "NOISE"}}

답변:"""

print("\n" + "="*80)
print("🌟 Solar 10.7B 모델 테스트 (한국 업스테이지 모델)")
print("="*80 + "\n")

solar_results = []
openai_results = []
solar_times = []
openai_times = []

for i, sample in enumerate(test_samples, 1):
    text = sample['text']
    expected = sample['expected']
    
    print(f"[{i}/{len(test_samples)}]")
    print(f"   텍스트: {text[:50]}...")
    print(f"   정답: {expected}")
    
    # Solar 테스트
    try:
        start = time.time()
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "solar:10.7b",
                "prompt": PROMPT.format(text=text),
                "stream": False,
                "options": {
                    "temperature": 0.0,
                    "num_predict": 50,
                    "stop": ["\n\n", "Note:"]
                }
            },
            timeout=60
        )
        solar_time = time.time() - start
        
        if response.status_code == 200:
            content = response.json()['response'].strip()
            
            # JSON 파싱
            try:
                solar_result = json.loads(content)['classification']
            except:
                # Fallback
                if 'REAL_CASE' in content:
                    solar_result = 'REAL_CASE'
                elif 'NEWS' in content:
                    solar_result = 'NEWS'
                elif 'NOISE' in content:
                    solar_result = 'NOISE'
                else:
                    solar_result = 'ERROR'
            
            solar_results.append(solar_result == expected)
            solar_times.append(solar_time)
            correct = '✅' if solar_result == expected else '❌'
            print(f"   Solar: {solar_result} {correct} ({solar_time:.2f}s)")
    except Exception as e:
        print(f"   Solar: ERROR - {str(e)[:40]}")
        solar_results.append(False)
    
    # OpenAI 비교
    try:
        start = time.time()
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={'Authorization': f'Bearer {OPENAI_KEY}', 'Content-Type': 'application/json'},
            json={
                'model': 'gpt-4o-mini',
                'messages': [
                    {'role': 'system', 'content': '피싱 분류 전문가'},
                    {'role': 'user', 'content': PROMPT.format(text=text)}
                ],
                'temperature': 0.0
            },
            timeout=30
        )
        openai_time = time.time() - start
        
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            try:
                openai_result = json.loads(content)['classification']
            except:
                openai_result = 'ERROR'
            openai_results.append(openai_result == expected)
            openai_times.append(openai_time)
            correct = '✅' if openai_result == expected else '❌'
            print(f"   OpenAI: {openai_result} {correct} ({openai_time:.2f}s)")
    except Exception as e:
        print(f"   OpenAI: ERROR")
        openai_results.append(False)
    
    print()
    time.sleep(0.3)

# 최종 결과
solar_acc = (sum(solar_results) / len(solar_results)) * 100
openai_acc = (sum(openai_results) / len(openai_results)) * 100
solar_avg = sum(solar_times) / len(solar_times) if solar_times else 0
openai_avg = sum(openai_times) / len(openai_times) if openai_times else 0

print("\n" + "="*80)
print("📊 최종 비교 결과")
print("="*80 + "\n")

print(f"🎯 정확도:")
print(f"   Solar:  {solar_acc:.0f}% ({sum(solar_results)}/{len(solar_results)})")
print(f"   OpenAI: {openai_acc:.0f}% ({sum(openai_results)}/{len(openai_results)})")
print()

print(f"⚡ 속도:")
print(f"   Solar:  {solar_avg:.2f}s/건")
print(f"   OpenAI: {openai_avg:.2f}s/건")
print(f"   → Solar가 {openai_avg/solar_avg:.1f}배 빠름!" if solar_avg < openai_avg else f"   → OpenAI가 {solar_avg/openai_avg:.1f}배 빠름!")
print()

print("="*80)
print("💡 종합 평가")
print("="*80)

if solar_acc >= 80:
    print(f"\n✅ **Solar 추천!**")
    print(f"   - 정확도 {solar_acc:.0f}%로 우수")
    print(f"   - 속도도 충분 ({solar_avg:.2f}s)")
    print(f"   - 무료 + 한국 모델")
    print(f"\n   💰 비용 절감: 일일 500개 × $0.06 = $30/월 → $0/월")
elif solar_acc >= 70:
    print(f"\n⚠️  **하이브리드 전략 추천**")
    print(f"   - Solar 정확도 {solar_acc:.0f}%로 준수")
    print(f"   - REAL_CASE 탐지: Solar (민감도 높음)")
    print(f"   - NEWS/NOISE 구분: OpenAI (정확도 높음)")
else:
    print(f"\n❌ **OpenAI 계속 사용 권장**")
    print(f"   - Solar 정확도 {solar_acc:.0f}%로 부족")
    print(f"   - 프롬프트 튜닝 또는 Qwen2 시도 권장")

print()

# 실용적 제안
print("="*80)
print("🚀 실전 적용 방안")
print("="*80)
print("""
1️⃣  **지금 (초기 데이터 5,000개)**
   → OpenAI 사용 (빠르고 정확)
   → 비용: 약 $0.64

2️⃣  **일일 크롤링 (500개/일)**
   → Solar/Qwen2 사용 (무료)
   → 월간 $30 절약!

3️⃣  **실시간 서비스**
   → Ollama FastAPI 통합
   → 응답속도 < 1초
""")

print("\n✅ 테스트 완료!\n")
