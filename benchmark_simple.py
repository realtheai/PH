#!/usr/bin/env python3
"""
OpenAI vs Ollama 벤치마크 (수동 샘플)
"""
import requests
import json
import time
import numpy as np
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_KEY = os.getenv('OPENAI_API_KEY')

# 테스트 샘플 (실제 피싱 사례)
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

CLASSIFY_PROMPT = """다음 텍스트가 피싱/스미싱인지 판단하세요.

REAL_CASE: 실제 피싱 사례
NEWS: 뉴스/기사
NOISE: 관련 없음

JSON으로만 답변: {{"classification": "REAL_CASE|NEWS|NOISE"}}

텍스트: {text}"""

print("\n" + "="*80)
print("🔬 OpenAI vs Ollama 성능 비교")
print("="*80 + "\n")
print(f"테스트 샘플: {len(test_samples)}개\n")

results = {'openai': [], 'ollama': []}
times = {'openai': [], 'ollama': []}

print("="*80)
print("🤖 분류 테스트")
print("="*80 + "\n")

for i, sample in enumerate(test_samples, 1):
    text = sample['text']
    expected = sample['expected']
    
    print(f"[{i}/{len(test_samples)}] {text[:40]}...")
    print(f"   정답: {expected}")
    
    # OpenAI
    try:
        start = time.time()
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={'Authorization': f'Bearer {OPENAI_KEY}', 'Content-Type': 'application/json'},
            json={
                'model': 'gpt-4o-mini',
                'messages': [
                    {'role': 'system', 'content': '피싱 분류 전문가'},
                    {'role': 'user', 'content': CLASSIFY_PROMPT.format(text=text)}
                ],
                'temperature': 0.1
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
            results['openai'].append(openai_result)
            times['openai'].append(openai_time)
            correct = '✅' if openai_result == expected else '❌'
            print(f"   OpenAI: {openai_result} {correct} ({openai_time:.2f}s)")
    except Exception as e:
        print(f"   OpenAI: ERROR - {str(e)[:50]}")
        results['openai'].append('ERROR')
    
    # Ollama
    try:
        start = time.time()
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3:8b",
                "prompt": CLASSIFY_PROMPT.format(text=text),
                "stream": False,
                "options": {"temperature": 0.1, "num_predict": 100}
            },
            timeout=60
        )
        ollama_time = time.time() - start
        
        if response.status_code == 200:
            content = response.json()['response']
            try:
                ollama_result = json.loads(content)['classification']
            except:
                if 'REAL_CASE' in content:
                    ollama_result = 'REAL_CASE'
                elif 'NEWS' in content:
                    ollama_result = 'NEWS'
                else:
                    ollama_result = 'NOISE'
            results['ollama'].append(ollama_result)
            times['ollama'].append(ollama_time)
            correct = '✅' if ollama_result == expected else '❌'
            print(f"   Ollama: {ollama_result} {correct} ({ollama_time:.2f}s)")
    except Exception as e:
        print(f"   Ollama: ERROR - {str(e)[:50]}")
        results['ollama'].append('ERROR')
    
    print()
    time.sleep(0.3)

# 결과 분석
print("\n" + "="*80)
print("📈 성능 비교 결과")
print("="*80 + "\n")

# 정확도
openai_correct = sum(1 for r, s in zip(results['openai'], test_samples) if r == s['expected'])
ollama_correct = sum(1 for r, s in zip(results['ollama'], test_samples) if r == s['expected'])

openai_accuracy = (openai_correct / len(test_samples)) * 100
ollama_accuracy = (ollama_correct / len(test_samples)) * 100

# 속도
openai_avg_time = np.mean(times['openai']) if times['openai'] else 0
ollama_avg_time = np.mean(times['ollama']) if times['ollama'] else 0

print("🎯 정확도:")
print(f"   OpenAI: {openai_accuracy:.1f}% ({openai_correct}/{len(test_samples)})")
print(f"   Ollama: {ollama_accuracy:.1f}% ({ollama_correct}/{len(test_samples)})")
print()

print("⚡ 속도:")
print(f"   OpenAI: {openai_avg_time:.2f}s/건")
print(f"   Ollama: {ollama_avg_time:.2f}s/건")
print(f"   속도 차이: Ollama가 {ollama_avg_time/openai_avg_time:.1f}배 느림")
print()

# 일치율
matches = sum(1 for o, l in zip(results['openai'], results['ollama']) if o == l and o != 'ERROR')
agreement = (matches / len(test_samples)) * 100

print("🤝 두 모델 일치율:")
print(f"   {agreement:.1f}% ({matches}/{len(test_samples)})")
print()

# 종합 평가
print("="*80)
print("💡 종합 평가")
print("="*80)
print(f"""
| 지표 | OpenAI | Ollama | 차이 |
|------|--------|--------|------|
| 정확도 | {openai_accuracy:.0f}% | {ollama_accuracy:.0f}% | {abs(openai_accuracy-ollama_accuracy):.0f}%p |
| 속도 | {openai_avg_time:.2f}s | {ollama_avg_time:.2f}s | {ollama_avg_time/openai_avg_time:.1f}배 |
| 비용 | 유료 | 무료 | - |
| 일치율 | - | {agreement:.0f}% | - |
""")

if ollama_accuracy >= 80:
    print("✅ **Ollama 추천!**")
    print(f"   - 정확도 {ollama_accuracy:.0f}%로 실용적")
    print(f"   - 무료 + 프라이버시 보호")
    print(f"   - 속도는 약간 느리지만 일일 크롤링엔 충분")
elif ollama_accuracy >= 70:
    print("⚠️  **하이브리드 추천**")
    print(f"   - OpenAI: 중요 데이터")
    print(f"   - Ollama: 일반 크롤링")
else:
    print("❌ **OpenAI 추천**")
    print(f"   - Ollama 정확도 {ollama_accuracy:.0f}%로 부족")

print("\n✅ 벤치마크 완료!\n")
