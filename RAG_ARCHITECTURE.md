# 🏗️ RAG 기반 피싱 탐지 서비스 아키텍처

## 📊 **수집된 데이터 (55,102건)**

```
웹 크롤링:     1,312건  (라이선스 안전)
  ├─ 네이버 API:  1,049건  (한국어 뉴스)
  ├─ 구글 뉴스:     120건  (한국어 뉴스)
  ├─ Reddit:       113건  (영어 사례)
  └─ 해외 뉴스:      30건  (영어 뉴스)

GitHub:       53,790건  (승인 필요)
  ├─ Voice_phising_KR:  1,200건  (한국어 대화)
  └─ KOR_phishing:    52,590건  (한국어 메시지)
```

---

## 🎯 **전체 시스템 아키텍처**

```
┌─────────────────────────────────────────────────────────┐
│                   사용자 인터페이스                        │
│  (웹/앱: 의심스러운 메시지/링크/전화번호 입력)              │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│              전처리 & 특징 추출 모듈                       │
│  • 텍스트 정제                                            │
│  • 키워드 추출 (전화번호, URL, 금융용어 등)                │
│  • 임베딩 생성                                            │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│              RAG (검색 증강 생성) 시스템                   │
│                                                          │
│  ┌──────────────────────────────────────────┐          │
│  │     Vector Database (Qdrant/Chroma)      │          │
│  │  • 55,102건 피싱 사례 임베딩               │          │
│  │  • 메타데이터 (출처, 날짜, 키워드)          │          │
│  │  • 유사도 검색 (Semantic Search)           │          │
│  └──────────────┬───────────────────────────┘          │
│                 │                                        │
│                 ▼                                        │
│  ┌──────────────────────────────────────────┐          │
│  │       Top-K 유사 사례 검색 (K=5~10)       │          │
│  └──────────────┬───────────────────────────┘          │
│                 │                                        │
│                 ▼                                        │
│  ┌──────────────────────────────────────────┐          │
│  │         LLM (GPT-4, Claude, Solar)       │          │
│  │  • 검색된 사례를 Context로 제공            │          │
│  │  • 피싱 여부 판단                          │          │
│  │  • 경고 메시지 생성                        │          │
│  └──────────────┬───────────────────────────┘          │
└─────────────────┼────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│                    판정 결과                              │
│  • 피싱 확률: 95%                                        │
│  • 유사 사례: "금융감독원 사칭 계좌이체 유도"              │
│  • 경고: "절대 계좌번호를 알려주지 마세요!"                │
│  • 대응 방법: 금감원 공식 번호로 재확인                   │
└─────────────────────────────────────────────────────────┘
```

---

## 📝 **단계별 구현 계획**

### **Phase 1: 데이터 전처리** (1~2일)

#### 1.1 데이터 통합
```python
# 모든 JSON 파일 병합
├─ naver_api_20260130_173420.json      (1,049건)
├─ news_all_20260130_144317.json       (120건)
├─ reddit_20260130_153743.json         (113건)
├─ social_all_20260130_153903.json     (30건)
└─ github/ (승인 후)
    ├─ Voice_phising_KR/               (1,200건)
    └─ KOR_phishing/                   (52,590건)

# 통합 포맷
{
  "id": "unique_id",
  "text": "피싱 메시지 또는 뉴스 내용",
  "source": "naver_api",
  "language": "ko",
  "keywords": ["피싱", "보이스피싱", "사칭"],
  "metadata": {
    "date": "2026-01-30",
    "category": "보이스피싱",
    "url": "...",
    "press": "..."
  }
}
```

#### 1.2 텍스트 정제
```python
# 정제 작업
• HTML 태그 제거
• 중복 제거
• 특수문자 정규화
• 전화번호/URL/계좌번호 패턴 추출
• 금융/피싱 키워드 추출
```

#### 1.3 라벨링 (자동 + 수동)
```python
# 자동 라벨링
├─ 보이스피싱 (전화 관련)
├─ 스미싱 (문자 관련)
├─ 메신저피싱 (카톡/텔레그램)
├─ 피싱사이트 (URL 관련)
├─ 금융사기 (계좌이체/대출)
└─ 기타
```

---

### **Phase 2: 임베딩 생성** (1일)

#### 2.1 한국어 임베딩 모델 선택

**옵션 1: OpenAI Embeddings** (추천)
```python
model: text-embedding-3-large
- 다국어 지원 (한국어 우수)
- 3,072 차원
- 비용: $0.13 / 1M tokens
```

**옵션 2: 한국어 전용 모델**
```python
model: jhgan/ko-sroberta-multitask
- 한국어 특화
- 768 차원
- 무료 (로컬 실행)
```

**옵션 3: Upstage Solar Embeddings**
```python
model: solar-embedding-1-large
- 한국어 최적화
- 4,096 차원
- 한국 기업 (Upstage)
```

#### 2.2 임베딩 생성 스크립트
```python
# scripts/generate_embeddings.py

from openai import OpenAI
import json

def generate_embeddings(texts):
    client = OpenAI()
    
    embeddings = []
    for text in texts:
        response = client.embeddings.create(
            model="text-embedding-3-large",
            input=text
        )
        embeddings.append(response.data[0].embedding)
    
    return embeddings

# 1,312건 처리 시간: 약 5~10분
# 비용: 약 $0.50~1.00
```

---

### **Phase 3: Vector DB 구축** (1~2일)

#### 3.1 Vector DB 선택

**옵션 1: Qdrant** (추천)
```yaml
장점:
  - 오픈소스
  - 로컬/클라우드 모두 지원
  - 빠른 검색 속도
  - 필터링 강력
  
설치:
  - Docker: qdrant/qdrant
  - Python: qdrant-client
```

**옵션 2: Chroma**
```yaml
장점:
  - 초경량
  - 로컬 우선
  - 쉬운 설정
  
단점:
  - 대규모 데이터에 제한적
```

**옵션 3: Pinecone**
```yaml
장점:
  - 완전 관리형
  - 확장성 우수
  
단점:
  - 유료 (무료는 1GB)
```

#### 3.2 Qdrant 설정
```python
# scripts/setup_vectordb.py

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# Qdrant 초기화
client = QdrantClient("localhost", port=6333)

# 컬렉션 생성
client.create_collection(
    collection_name="phishing_cases",
    vectors_config=VectorParams(
        size=3072,  # text-embedding-3-large
        distance=Distance.COSINE
    )
)

# 데이터 삽입
points = []
for i, (text, embedding, metadata) in enumerate(data):
    points.append({
        "id": i,
        "vector": embedding,
        "payload": {
            "text": text,
            "source": metadata["source"],
            "keywords": metadata["keywords"],
            "date": metadata["date"]
        }
    })

client.upsert(
    collection_name="phishing_cases",
    points=points
)
```

---

### **Phase 4: RAG 시스템 구축** (2~3일)

#### 4.1 RAG 파이프라인

```python
# src/rag_pipeline.py

from openai import OpenAI
from qdrant_client import QdrantClient

class PhishingRAG:
    def __init__(self):
        self.openai_client = OpenAI()
        self.qdrant_client = QdrantClient("localhost", port=6333)
    
    def embed_query(self, query: str):
        """쿼리 임베딩 생성"""
        response = self.openai_client.embeddings.create(
            model="text-embedding-3-large",
            input=query
        )
        return response.data[0].embedding
    
    def search_similar_cases(self, query: str, top_k: int = 5):
        """유사 피싱 사례 검색"""
        query_vector = self.embed_query(query)
        
        results = self.qdrant_client.search(
            collection_name="phishing_cases",
            query_vector=query_vector,
            limit=top_k
        )
        
        return results
    
    def analyze_phishing(self, user_input: str):
        """피싱 여부 판단"""
        # 1. 유사 사례 검색
        similar_cases = self.search_similar_cases(user_input, top_k=5)
        
        # 2. Context 구성
        context = "\n\n".join([
            f"[사례 {i+1}] {case.payload['text'][:200]}..."
            for i, case in enumerate(similar_cases)
        ])
        
        # 3. LLM에 질의
        prompt = f"""
당신은 피싱 탐지 전문가입니다.

사용자가 받은 메시지:
{user_input}

유사한 피싱 사례:
{context}

위 정보를 바탕으로 다음을 분석해주세요:
1. 피싱 가능성 (0~100%)
2. 피싱 유형 (보이스피싱/스미싱/메신저피싱/기타)
3. 위험 요소 (의심스러운 부분)
4. 대응 방법

JSON 형식으로 답변:
{{
  "is_phishing": true/false,
  "confidence": 95,
  "phishing_type": "보이스피싱",
  "risk_factors": ["공공기관 사칭", "계좌이체 요구", "긴급 협박"],
  "recommendation": "절대 계좌번호를 알려주지 마세요...",
  "similar_cases": [...]
}}
"""
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
```

---

### **Phase 5: 서비스 개발** (3~5일)

#### 5.1 백엔드 API (FastAPI)

```python
# src/api.py

from fastapi import FastAPI
from pydantic import BaseModel
from rag_pipeline import PhishingRAG

app = FastAPI()
rag = PhishingRAG()

class CheckRequest(BaseModel):
    message: str
    phone_number: str = None
    url: str = None

@app.post("/api/check")
async def check_phishing(request: CheckRequest):
    """피싱 검사 API"""
    result = rag.analyze_phishing(request.message)
    return result

@app.get("/api/stats")
async def get_stats():
    """통계 API"""
    return {
        "total_cases": 55102,
        "sources": {
            "naver": 1049,
            "google": 120,
            "reddit": 113,
            "github": 53790
        }
    }
```

#### 5.2 프론트엔드 (Streamlit/Gradio)

```python
# src/app.py

import streamlit as st
import requests

st.title("🛡️ 피싱 탐지 서비스")
st.write("의심스러운 메시지를 입력하세요")

# 사용자 입력
user_input = st.text_area(
    "메시지 내용",
    placeholder="예) 안녕하세요 금융감독원입니다. 귀하의 계좌가..."
)

if st.button("검사하기"):
    if user_input:
        # API 호출
        response = requests.post(
            "http://localhost:8000/api/check",
            json={"message": user_input}
        )
        result = response.json()
        
        # 결과 표시
        if result["is_phishing"]:
            st.error(f"⚠️ 피싱 의심! ({result['confidence']}%)")
            st.write(f"**유형**: {result['phishing_type']}")
            st.write(f"**위험 요소**:")
            for factor in result['risk_factors']:
                st.write(f"  - {factor}")
            st.write(f"**대응 방법**: {result['recommendation']}")
        else:
            st.success("✅ 안전한 메시지입니다")
```

---

## 🔍 **실제 사용 시나리오**

### 시나리오 1: 보이스피싱

**사용자 입력:**
```
"안녕하세요 금융감독원입니다. 
귀하의 계좌가 해킹당해 긴급히 안전계좌로 이체가 필요합니다.
다음 번호로 전화주세요: 02-1234-5678"
```

**시스템 처리:**
1. 임베딩 생성
2. Vector DB에서 유사 사례 검색
   - "금융감독원 사칭 계좌이체 유도" (유사도 95%)
   - "공공기관 사칭 긴급 협박" (유사도 92%)
3. LLM 분석

**결과:**
```json
{
  "is_phishing": true,
  "confidence": 98,
  "phishing_type": "보이스피싱 (공공기관 사칭)",
  "risk_factors": [
    "금융감독원 사칭",
    "긴급성 강조",
    "안전계좌 이체 요구",
    "비공식 전화번호"
  ],
  "recommendation": "절대 전화하지 마세요! 금융감독원은 전화로 계좌이체를 요구하지 않습니다. 공식 홈페이지(www.fss.or.kr)에서 확인하세요.",
  "official_contact": "금융감독원: 1332"
}
```

---

### 시나리오 2: 택배 스미싱

**사용자 입력:**
```
"[CJ대한통운] 고객님의 택배가 보관중입니다.
확인: http://cjtacksongc.com/track?id=12345"
```

**결과:**
```json
{
  "is_phishing": true,
  "confidence": 99,
  "phishing_type": "스미싱 (택배 사칭)",
  "risk_factors": [
    "의심스러운 URL (정식 도메인 아님)",
    "철자 오류 (tacksongc → taekbaesong)",
    "단축 링크 미사용"
  ],
  "recommendation": "링크를 클릭하지 마세요! CJ대한통운 공식 앱이나 웹사이트에서 직접 확인하세요.",
  "official_contact": "CJ대한통운: 1588-1255"
}
```

---

## 📊 **예상 성능**

### 검색 속도
```
Vector DB 검색: ~50ms
임베딩 생성: ~100ms
LLM 응답: ~2s
━━━━━━━━━━━━━━━━━━
총 응답 시간: ~2.2s
```

### 정확도 (예상)
```
피싱 탐지율: 95%+
False Positive: <5%
False Negative: <3%
```

---

## 💰 **비용 예상**

### 초기 구축 비용
```
임베딩 생성 (55K건):
  - OpenAI: ~$2~5
  - 로컬 모델: 무료

Vector DB:
  - Qdrant (로컬): 무료
  - Pinecone: ~$70/month
```

### 운영 비용 (월 1만 쿼리 기준)
```
임베딩: $0.50
LLM (GPT-4): $50~100
인프라: $10~50
━━━━━━━━━━━━━━━
총: $60~150/month
```

---

## 🚀 **타임라인**

```
Week 1:
  Day 1-2: 데이터 전처리
  Day 3-4: 임베딩 생성 + Vector DB 구축
  Day 5-7: RAG 파이프라인 구축

Week 2:
  Day 8-10: 백엔드 API 개발
  Day 11-12: 프론트엔드 개발
  Day 13-14: 테스트 & 디버깅

Week 3:
  Day 15-17: 성능 최적화
  Day 18-19: 문서화
  Day 20-21: 데모 & 발표 준비
```

---

## 📝 **다음 단계**

1. **즉시 시작**: 데이터 전처리 스크립트 작성
2. **환경 설정**: Qdrant Docker 설치
3. **API 키 준비**: OpenAI API Key
4. **임베딩 모델 선택**: OpenAI vs 로컬 모델

**지금 바로 시작할까요?** 🚀
