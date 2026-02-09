#!/usr/bin/env python3
"""
OpenAI vs Ollama 성능 비교 벤치마크
- 실제 데이터 샘플로 테스트
- 정확도, 속도, 품질 비교
"""
import os
import sys
import requests
import json
import time
from datetime import datetime
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
OPENAI_KEY = os.getenv('OPENAI_API_KEY')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

print("\n" + "="*80)
print("🔬 OpenAI vs Ollama 성능 비교 벤치마크")
print("="*80 + "\n")

# 1. 샘플 데이터 가져오기
print("📊 테스트 데이터 준비 중...\n")

# 실제 이미지 OCR 텍스트 샘플 가져오기
url = f"{SUPABASE_URL}/rest/v1/phishing_images"
params = {
    'select': 'id,ocr_text',
    'ocr_text': 'not.is.null',
    'limit': 20,
    'order': 'random()'
}
response = requests.get(url, headers=HEADERS, params=params)
data = response.json()
samples = data[:10] if isinstance(data, list) else []  # 10개만 테스트

print(f"✅ 테스트 샘플: {len(samples)}개\n")

# 분류 프롬프트
CLASSIFY_PROMPT = """다음 OCR 텍스트를 분석하여 피싱/스미싱 관련성을 판단하세요.

REAL_CASE: 실제 피싱 사례 (문자, 카톡 등)
NEWS: 피싱 뉴스/기사  
NOISE: 관련 없음

JSON으로만 답변: {{"classification": "REAL_CASE|NEWS|NOISE"}}

텍스트: {text}"""

# 결과 저장
results = {
    'openai': {'classifications': [], 'embeddings': [], 'times': []},
    'ollama': {'classifications': [], 'embeddings': [], 'times': []}
}

print("="*80)
print("🤖 분류 테스트")
print("="*80 + "\n")

for i, sample in enumerate(samples, 1):
    sample_id = sample['id']
    text = sample['ocr_text'][:300]  # 처음 300자만
    
    print(f"[{i}/{len(samples)}] ID:{sample_id}")
    print(f"   텍스트: {text[:50]}...")
    
    # OpenAI 분류
    try:
        start = time.time()
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {OPENAI_KEY}',
                'Content-Type': 'application/json'
            },
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
            results['openai']['times'].append(openai_time)
            results['openai']['classifications'].append(openai_result)
            print(f"   OpenAI: {openai_result} ({openai_time:.2f}s)")
        else:
            print(f"   OpenAI: ERROR")
            results['openai']['classifications'].append('ERROR')
    except Exception as e:
        print(f"   OpenAI: ERROR - {str(e)[:30]}")
        results['openai']['classifications'].append('ERROR')
    
    # Ollama 분류
    try:
        start = time.time()
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3:8b",
                "prompt": CLASSIFY_PROMPT.format(text=text),
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 100
                }
            },
            timeout=60
        )
        ollama_time = time.time() - start
        
        if response.status_code == 200:
            content = response.json()['response']
            try:
                ollama_result = json.loads(content)['classification']
            except:
                # JSON 파싱 실패 시 텍스트에서 추출
                if 'REAL_CASE' in content:
                    ollama_result = 'REAL_CASE'
                elif 'NEWS' in content:
                    ollama_result = 'NEWS'
                else:
                    ollama_result = 'NOISE'
            results['ollama']['times'].append(ollama_time)
            results['ollama']['classifications'].append(ollama_result)
            print(f"   Ollama: {ollama_result} ({ollama_time:.2f}s)")
        else:
            print(f"   Ollama: ERROR")
            results['ollama']['classifications'].append('ERROR')
    except Exception as e:
        print(f"   Ollama: ERROR - {str(e)[:30]}")
        results['ollama']['classifications'].append('ERROR')
    
    # 일치 여부
    if (results['openai']['classifications'][-1] == results['ollama']['classifications'][-1] 
        and 'ERROR' not in results['openai']['classifications'][-1]):
        print(f"   ✅ 일치!")
    else:
        print(f"   ⚠️  불일치")
    
    print()
    time.sleep(0.5)

print("\n" + "="*80)
print("📊 임베딩 테스트 (5개 샘플)")
print("="*80 + "\n")

# 임베딩 테스트 (5개만)
for i, sample in enumerate(samples[:5], 1):
    text = sample['ocr_text'][:300]
    
    print(f"[{i}/5] 임베딩 생성 중...")
    
    # OpenAI 임베딩
    try:
        start = time.time()
        response = requests.post(
            'https://api.openai.com/v1/embeddings',
            headers={
                'Authorization': f'Bearer {OPENAI_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'text-embedding-3-small',
                'input': text
            },
            timeout=30
        )
        openai_time = time.time() - start
        
        if response.status_code == 200:
            openai_emb = response.json()['data'][0]['embedding']
            results['openai']['embeddings'].append(openai_emb)
            print(f"   OpenAI: {len(openai_emb)}차원 ({openai_time:.2f}s)")
    except Exception as e:
        print(f"   OpenAI: ERROR")
    
    # Ollama 임베딩
    try:
        start = time.time()
        response = requests.post(
            "http://localhost:11434/api/embeddings",
            json={
                "model": "bge-m3:567m",
                "prompt": text
            },
            timeout=30
        )
        ollama_time = time.time() - start
        
        if response.status_code == 200:
            ollama_emb = response.json()['embedding']
            results['ollama']['embeddings'].append(ollama_emb)
            print(f"   Ollama: {len(ollama_emb)}차원 ({ollama_time:.2f}s)")
    except Exception as e:
        print(f"   Ollama: ERROR")
    
    print()

# 결과 분석
print("\n" + "="*80)
print("📈 성능 비교 결과")
print("="*80 + "\n")

# 분류 일치율
openai_cls = [c for c in results['openai']['classifications'] if c != 'ERROR']
ollama_cls = [c for c in results['ollama']['classifications'] if c != 'ERROR']
matches = sum(1 for o, l in zip(openai_cls, ollama_cls) if o == l)
agreement = (matches / len(openai_cls)) * 100 if openai_cls else 0

print("🤖 분류 성능:")
print(f"   일치율: {agreement:.1f}% ({matches}/{len(openai_cls)})")
print(f"   OpenAI 속도: {np.mean(results['openai']['times']):.2f}s/건")
print(f"   Ollama 속도: {np.mean(results['ollama']['times']):.2f}s/건")
print()

# 임베딩 품질 (유사도 비교)
if results['openai']['embeddings'] and results['ollama']['embeddings']:
    # 차원 맞추기 위해 정규화 후 비교
    print("📊 임베딩 품질:")
    print(f"   OpenAI: {len(results['openai']['embeddings'][0])}차원")
    print(f"   Ollama: {len(results['ollama']['embeddings'][0])}차원")
    print(f"   → 차원이 다르지만 각각 독립적으로 사용 가능")
    print()

# 종합 평가
print("="*80)
print("💡 종합 평가")
print("="*80)
print(f"""
| 지표 | OpenAI | Ollama | 승자 |
|------|--------|--------|------|
| 속도 | {np.mean(results['openai']['times']):.2f}s | {np.mean(results['ollama']['times']):.2f}s | {'OpenAI' if np.mean(results['openai']['times']) < np.mean(results['ollama']['times']) else 'Ollama'} |
| 일치율 | 100% | {agreement:.0f}% | {'OpenAI' if agreement < 95 else '동등'} |
| 비용 | 유료 | 무료 | Ollama |
| 프라이버시 | 외부 전송 | 로컬 | Ollama |

📊 권장 사항:
""")

if agreement >= 90:
    print("✅ Ollama 성능 우수! 일일 크롤링에 사용 추천")
    print(f"   - 일치율 {agreement:.0f}%로 신뢰 가능")
    print(f"   - 속도 차이: 약 {np.mean(results['ollama']['times'])/np.mean(results['openai']['times']):.1f}배")
elif agreement >= 80:
    print("⚠️  Ollama 성능 준수. 하이브리드 사용 권장")
    print(f"   - 중요 데이터: OpenAI")
    print(f"   - 일반 크롤링: Ollama")
else:
    print("❌ Ollama 성능 부족. OpenAI 사용 권장")
    print(f"   - 일치율 {agreement:.0f}%로 낮음")

print("\n✅ 벤치마크 완료!\n")

# 결과 저장
with open('/tmp/benchmark_results.json', 'w') as f:
    json.dump({
        'agreement': agreement,
        'openai_avg_time': np.mean(results['openai']['times']),
        'ollama_avg_time': np.mean(results['ollama']['times']),
        'samples_tested': len(samples)
    }, f, indent=2)

print("📁 결과 저장: /tmp/benchmark_results.json\n")
