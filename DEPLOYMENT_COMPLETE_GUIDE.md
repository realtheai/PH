## 🔍 전체 모델/서비스 의존성 분석 (수정)

### 📊 완전한 의존성 맵

| 기능 | 모델/서비스 | 타입 | 로컬 서버 필요? | 배포 시 |
|------|------------|------|---------------|---------|
| **OCR (이미지→텍스트)** | OpenAI GPT-4o-mini Vision | ☁️ API | ❌ 불필요 | ✅ **API 키만** |
| **OCR Fallback** | Google Gemini 2.5 Flash | ☁️ API | ❌ 불필요 | ✅ **API 키만** |
| **LLM 분석** | OpenAI GPT-4o-mini | ☁️ API | ❌ 불필요 | ✅ **API 키만** |
| **임베딩 (검색)** | BGE-M3 (Ollama) | 🖥️ 로컬 | ⚠️ **필요** | ❌ **문제!** |
| **URL 검사** | Google Safe Browsing | ☁️ API | ❌ 불필요 | ✅ **API 키만** |
| **데이터베이스** | Supabase PostgreSQL | ☁️ 클라우드 | ❌ 불필요 | ✅ **URL만** |

---

## ✅ 좋은 소식: OCR은 문제 없음!

### OCR 처리 방식 (이미 완료된 데이터)
```python
# scripts/process_images_dual_ocr.py
# 1차: OpenAI Vision API
response = requests.post(
    "https://api.openai.com/v1/chat/completions",
    json={"model": "gpt-4o-mini", ...}
)

# 2차 (Fallback): Google Gemini Vision API
response = requests.post(
    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}",
    ...
)
```

**→ 모두 클라우드 API! 로컬 서버 불필요 ✅**

---

## ⚠️ 유일한 문제: 벡터 검색 (임베딩)

### 현재 상황

```python
# backend/app/core/embedder.py
# ❌ 로컬 Ollama 서버 필요
requests.post(
    "http://localhost:11434/api/embeddings",
    json={"model": "bge-m3:567m", "prompt": text}
)
```

**이것만 해결하면 GitHub Actions 배포 가능!**

---

## 🚀 GitHub Actions 배포 전략

### 시나리오 1: OpenAI 임베딩 전환 (추천 ⭐⭐⭐)

#### 필요한 것
```yaml
# 환경 변수만 설정
OPENAI_API_KEY: xxx
GEMINI_API_KEY: xxx (× 8개)
GOOGLE_SAFE_BROWSING_API_KEY: xxx
SUPABASE_URL: xxx
SUPABASE_ANON_KEY: xxx
```

#### 작업
1. `embedder.py` OpenAI로 전환 (5분)
2. DB 1,373개 재임베딩 (10분, $0.003)
3. GitHub Actions 배포 (5분)

**총 소요 시간: 20분**  
**총 비용: 약 3원**

---

### 시나리오 2: 벡터 검색 비활성화

#### 장점
- 즉시 배포 가능 (수정 불필요)
- 비용 제로

#### 단점
- 유사 사례 검색 못함
- 정확도 약간 하락

#### 수정 방법
```python
# backend/app/api/v1/analyze.py
# 벡터 검색 부분 주석 처리
# try:
#     query_embedding = embedder.create_embedding(message)
#     ...
# except:
#     pass
```

---

### 시나리오 3: HuggingFace Inference API (무료)

#### 아이디어
```python
# BGE-M3를 HuggingFace Inference API로 사용
import requests

API_URL = "https://api-inference.huggingface.co/models/BAAI/bge-m3"
headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()
```

#### 장점
- 무료 (제한적)
- 서버 불필요
- BGE-M3 그대로 사용

#### 단점
- 속도 느림
- Rate limit 있음

---

## 💡 최종 추천

### 단계별 접근

#### 1단계: 임시 배포 (벡터 검색 비활성화)
- **소요 시간**: 5분
- **비용**: $0
- **목적**: 일단 서비스 띄우기

```python
# 벡터 검색만 주석 처리
# similar_cases = []  # 빈 배열로 처리
```

#### 2단계: OpenAI 임베딩 전환 (프로덕션)
- **소요 시간**: 20분
- **비용**: ~$0.003
- **목적**: 완전한 기능

```python
# OpenAI embedding API 사용
self.client.embeddings.create(
    model="text-embedding-3-small",
    input=text
)
```

---

## 📋 필요한 API 키 정리

### GitHub Secrets 설정 필요

```bash
# OpenAI (필수)
OPENAI_API_KEY=sk-proj-xxx

# Google (필수)
GOOGLE_SAFE_BROWSING_API_KEY=AIzaSyxxx
GEMINI_API_KEY=AIzaSyxxx
GEMINI_API_KEY_2=AIzaSyxxx
GEMINI_API_KEY_3=AIzaSyxxx
# ... (8개까지)

# Supabase (필수)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJhbxxx
SUPABASE_SERVICE_ROLE_KEY=eyJhbxxx

# HuggingFace (옵션 3 선택 시)
HUGGINGFACE_TOKEN=hf_xxx
```

---

## 🎯 결론

**OCR은 문제 없습니다!** ✅
- 이미 OpenAI/Gemini API 사용 중
- 로컬 서버 불필요

**유일한 문제: 벡터 검색 (임베딩)** ⚠️
- 현재: Ollama BGE-M3 (로컬 서버)
- 해결책: OpenAI 임베딩 전환 (추천)

어떻게 진행하시겠습니까?
