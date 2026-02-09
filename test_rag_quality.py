#!/usr/bin/env python3
"""
RAG 품질 비교: OpenAI vs Ollama
- 실제 검색 시나리오 테스트
- Top-K 중첩률 측정
- 검색 품질 평가
"""
import requests
import json
import time
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_KEY = os.getenv('OPENAI_API_KEY')

# 실제 피싱 메시지 DB (시뮬레이션)
database = [
    "택배가 도착했습니다. 주소지 변경: http://bit.ly/abc",
    "안녕하세요 아들이에요. 급하게 돈 필요해요. 카톡 안돼서 문자해요",
    "경찰청 보이스피싱 예방 캠페인 실시 발표",
    "[Web발신] 국민연금 환급금 조회하세요",
    "금융감독원입니다. 계좌가 범죄에 연루되었습니다",
    "오늘 날씨가 좋네요",
    "엄마예요 핸드폰 고장나서 친구폰 씁니다",
    "삼성전자 신제품 출시",
    "부고 문자입니다. 부의금 계좌 안내드립니다",
    "경찰관입니다. 즉시 연락주세요"
]

# 사용자 검색 쿼리
search_queries = [
    {"query": "택배 주소 변경 문자", "relevant": [0, 3]},  # 택배 관련
    {"query": "가족 사칭 카톡", "relevant": [1, 6]},        # 가족 사칭
    {"query": "경찰청 캠페인", "relevant": [2]},             # 뉴스
    {"query": "금융감독원 사칭", "relevant": [4, 9]},        # 기관 사칭
]

print("\n" + "="*80)
print("🔬 RAG 검색 품질 비교: OpenAI vs Ollama BGE-M3")
print("="*80 + "\n")

def get_embeddings_batch(texts, use_ollama=False):
    """배치 임베딩 생성"""
    embeddings = []
    
    for text in texts:
        if use_ollama:
            response = requests.post(
                "http://localhost:11434/api/embeddings",
                json={"model": "bge-m3:567m", "prompt": text},
                timeout=30
            )
            if response.status_code == 200:
                embeddings.append(response.json()['embedding'])
        else:
            response = requests.post(
                'https://api.openai.com/v1/embeddings',
                headers={'Authorization': f'Bearer {OPENAI_KEY}', 'Content-Type': 'application/json'},
                json={'model': 'text-embedding-3-small', 'input': text},
                timeout=30
            )
            if response.status_code == 200:
                embeddings.append(response.json()['data'][0]['embedding'])
        time.sleep(0.1)
    
    return embeddings

print("1️⃣  데이터베이스 임베딩 생성 중...\n")
print(f"   데이터베이스: {len(database)}개 문서")

# OpenAI 임베딩
print("   OpenAI 임베딩 생성 중...")
start = time.time()
openai_db_embeddings = get_embeddings_batch(database, use_ollama=False)
openai_db_time = time.time() - start
print(f"   ✅ OpenAI 완료 ({openai_db_time:.2f}s)")

# Ollama 임베딩
print("   Ollama 임베딩 생성 중...")
start = time.time()
ollama_db_embeddings = get_embeddings_batch(database, use_ollama=True)
ollama_db_time = time.time() - start
print(f"   ✅ Ollama 완료 ({ollama_db_time:.2f}s)")

print()

# 2. 검색 테스트
print("="*80)
print("2️⃣  검색 품질 테스트 (Top-3)")
print("="*80 + "\n")

openai_scores = []
ollama_scores = []

for i, search in enumerate(search_queries, 1):
    query = search['query']
    relevant_docs = search['relevant']
    
    print(f"[{i}/{len(search_queries)}] 검색: \"{query}\"")
    print(f"   정답: {relevant_docs}")
    
    # OpenAI 검색
    query_emb_openai = get_embeddings_batch([query], use_ollama=False)[0]
    similarities_openai = cosine_similarity([query_emb_openai], openai_db_embeddings)[0]
    top3_openai = np.argsort(similarities_openai)[-3:][::-1].tolist()
    
    print(f"   OpenAI Top-3: {top3_openai}")
    print(f"      유사도: {[f'{similarities_openai[idx]:.3f}' for idx in top3_openai]}")
    
    # 정확도 계산 (Top-3에 정답이 몇 개 포함되는가)
    openai_hits = len(set(top3_openai) & set(relevant_docs))
    openai_precision = openai_hits / len(relevant_docs)
    print(f"      정확도: {openai_hits}/{len(relevant_docs)} {'✅' if openai_hits > 0 else '❌'}")
    openai_scores.append(openai_precision)
    
    # Ollama 검색
    query_emb_ollama = get_embeddings_batch([query], use_ollama=True)[0]
    similarities_ollama = cosine_similarity([query_emb_ollama], ollama_db_embeddings)[0]
    top3_ollama = np.argsort(similarities_ollama)[-3:][::-1].tolist()
    
    print(f"   Ollama Top-3: {top3_ollama}")
    print(f"      유사도: {[f'{similarities_ollama[idx]:.3f}' for idx in top3_ollama]}")
    
    ollama_hits = len(set(top3_ollama) & set(relevant_docs))
    ollama_precision = ollama_hits / len(relevant_docs)
    print(f"      정확도: {ollama_hits}/{len(relevant_docs)} {'✅' if ollama_hits > 0 else '❌'}")
    ollama_scores.append(ollama_precision)
    
    # Top-3 중첩률
    overlap = len(set(top3_openai) & set(top3_ollama))
    print(f"   Top-3 중첩: {overlap}/3 ({overlap/3*100:.0f}%)")
    
    print()

# 3. 최종 평가
print("="*80)
print("📊 RAG 검색 품질 평가")
print("="*80 + "\n")

openai_avg_precision = np.mean(openai_scores) * 100
ollama_avg_precision = np.mean(ollama_scores) * 100

print(f"🎯 검색 정확도 (Precision@3):")
print(f"   OpenAI: {openai_avg_precision:.1f}%")
print(f"   Ollama: {ollama_avg_precision:.1f}%")
print()

print(f"⚡ 속도:")
print(f"   OpenAI: {openai_db_time/len(database):.3f}s/건")
print(f"   Ollama: {ollama_db_time/len(database):.3f}s/건")
print()

print("="*80)
print("💡 최종 결론")
print("="*80)

if ollama_avg_precision >= openai_avg_precision * 0.9:  # 90% 이상이면
    print(f"\n✅ **Ollama BGE-M3 강력 추천!**")
    print(f"   - RAG 검색 품질: {ollama_avg_precision:.0f}% (OpenAI {openai_avg_precision:.0f}%)")
    print(f"   - 속도: {ollama_db_time/len(database):.3f}s/건")
    print(f"   - 비용: 무료")
    print(f"   - 저장공간: 33% 절약")
    print(f"\n   💰 절감 효과:")
    print(f"      - 초기 5,000개: $0.10 절약")
    print(f"      - 일일 500개: $0.01/일 × 365일 = $3.65/년 절약")
elif ollama_avg_precision >= openai_avg_precision * 0.7:  # 70% 이상
    print(f"\n⚠️  **조건부 추천**")
    print(f"   - Ollama: {ollama_avg_precision:.0f}% (OpenAI 대비 {ollama_avg_precision/openai_avg_precision*100:.0f}%)")
    print(f"   - 일일 크롤링: Ollama (비용 절감)")
    print(f"   - 중요 검색: OpenAI (품질 우선)")
else:
    print(f"\n❌ **OpenAI 사용 권장**")
    print(f"   - Ollama 품질 {ollama_avg_precision:.0f}% (OpenAI 대비 {ollama_avg_precision/openai_avg_precision*100:.0f}%)")
    print(f"   - RAG 검색 품질이 너무 낮음")

print("\n" + "="*80 + "\n")
