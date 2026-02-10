# 🛡️ 피싱체커 (PhishingChecker)

AI 기반 피싱/스미싱 실시간 탐지 시스템 - 의심 메시지를 바로 확인하세요

[![Backend Deploy](https://github.com/realtheai/PH/actions/workflows/deploy-backend.yml/badge.svg)](https://github.com/realtheai/PH/actions/workflows/deploy-backend.yml)
[![Data Pipeline](https://github.com/realtheai/PH/actions/workflows/daily-data-pipeline.yml/badge.svg)](https://github.com/realtheai/PH/actions/workflows/daily-data-pipeline.yml)

## 🌐 배포된 서비스

- **웹 앱**: [phishing-checker-one.vercel.app](https://phishing-checker-one.vercel.app)
- **백엔드 API**: [https://ph-production-4b6a.up.railway.app](https://ph-production-4b6a.up.railway.app)
- **모바일 앱**: APK 다운로드 (`frontend/android/app/build/outputs/apk/debug/app-debug.apk`)

---

## 📱 주요 기능

### ✅ **실시간 메시지 분석**
- 의심스러운 문자/메시지를 입력하면 즉시 피싱 여부 판단
- 위험도를 5단계로 분류 (안전/낮음/보통/높음/매우높음)
- 피싱 유형 자동 분류 (11가지 유형)

### 🎯 **3단계 정밀 분석**
1. **규칙 기반 검사**: 300+ 피싱 키워드 패턴 매칭
2. **벡터 검색 (RAG)**: pgvector + HNSW 인덱스로 7,137개 실제 피싱 사례 및 뉴스 전체 검색
3. **LLM 분석**: OpenAI GPT-4o-mini 기반 문맥 이해 및 판단

### 🔍 **상세 분석 결과**
- AI 확신도 (0-100%)
- 유사한 실제 피싱 사례 개수
- 구체적인 대응 권장사항
- 피싱 유형별 맞춤 설명

### 📊 **편리한 기능**
- 다크 모드 지원
- 검사 내역 자동 저장
- 결과 공유 (Web Share API)
- 모바일 앱 (Android APK)

---

## 🛠️ 기술 스택

### **Frontend (웹 + 모바일)**
| 기술 | 버전 | 용도 |
|------|------|------|
| **Next.js** | 15.1.5 | React 프레임워크 (App Router) |
| **React** | 19 | UI 라이브러리 |
| **TypeScript** | 5.x | 타입 안정성 |
| **Tailwind CSS** | 4.0.0 | 스타일링 (다크 모드 포함) |
| **Capacitor** | 6.2.0 | 네이티브 모바일 앱 (Android) |
| **Vercel** | - | 웹 배포 플랫폼 |

**특징:**
- Static HTML Export (모바일용) + Server Rendering (웹용) 조건부 빌드
- Material Symbols Icons 사용
- 반응형 디자인 (모바일 우선)

### **Backend (API 서버)**
| 기술 | 버전 | 용도 |
|------|------|------|
| **FastAPI** | 0.115.6 | Python 웹 프레임워크 |
| **Python** | 3.11 | 백엔드 언어 |
| **OpenAI API** | - | GPT-4o-mini (LLM), text-embedding-3-small (임베딩) |
| **Supabase** | - | PostgreSQL + pgvector (벡터 검색) |
| **Google Safe Browsing** | - | URL 위험도 검사 |
| **Railway.app** | - | 백엔드 배포 플랫폼 |
| **Docker** | - | 컨테이너화 |

**주요 라이브러리:**
- `httpx`: 비동기 HTTP 클라이언트
- `uvicorn`: ASGI 서버
- `python-dotenv`: 환경 변수 관리

### **데이터베이스**
| 기술 | 용도 |
|------|------|
| **Supabase (PostgreSQL)** | 실제 피싱 사례 저장 |
| **pgvector** | 벡터 임베딩 저장 및 유사도 검색 |
| **OpenAI Embeddings** | 텍스트 → 벡터 변환 (1536차원) |

### **CI/CD & 자동화**
| 도구 | 용도 |
|------|------|
| **GitHub Actions** | 자동 배포 + 데이터 파이프라인 |
| **Vercel Git Integration** | 프론트엔드 자동 배포 (main push 시) |
| **Railway Git Integration** | 백엔드 자동 배포 (backend/ 변경 시) |

---

## 📊 데이터 수집 출처

### **실제 피싱 사례: 7,137개 (임베딩 완료)**

| 출처 | 임베딩 완료 | 벡터 검색 방식 | 검색 범위 |
|------|----------|-------------|----------|
| **뉴스 (네이버, 구글, Reddit)** | **5,800개** | pgvector RPC + HNSW | **전체 5,800개** ✅ |
| **Google Images (OCR)** | **1,337개** | pgvector RPC + HNSW | **전체 1,337개** ✅ |
| **총계** | **7,137개** | - | - |

**벡터 검색 최적화:**
- **뉴스 (네이버/구글/Reddit, 5,800개)**: Supabase `find_similar_phishing` RPC 함수, HNSW 인덱스로 **전체 검색** (~100ms)
- **이미지 (1,337개)**: Supabase `find_similar_phishing_images` RPC 함수, HNSW 인덱스로 **전체 검색** (~100ms)
- **threshold**: 코사인 유사도 ≥ 0.3 (30%)
- **결과**: 뉴스 3개 + 이미지 2개 = 상위 5개 유사 사례 반환
- **Fallback**: RPC 실패 시 자동으로 클라이언트 샘플링 방식으로 전환

> **📌 Note**: 전체 11,804개 수집 중 7,137개가 임베딩 완료 (완료율 60.5%)

### **데이터 처리 파이프라인**

```
1. 크롤링 (scripts/)
   ├─ 네이버 뉴스 API (scripts/crawl_naver_api.py)
   ├─ 구글 뉴스 API (scripts/crawl_google_news.py, crawl_international_news.py)
   ├─ Reddit (scripts/daily_reddit.py)
   └─ Google Images + OCR (scripts/process_images_ocr.py)
        └─ Gemini Vision API (텍스트 추출)

2. 전처리
   ├─ 중복 제거 (scripts/deduplicate_data.py)
   ├─ 분류 (scripts/classify_phishing_type.py)
   └─ 번역 (한/영) (scripts/translate_with_openai.py)

3. 임베딩 & 저장
   ├─ OpenAI text-embedding-3-small (1536차원)
   └─ Supabase (PostgreSQL + pgvector)
```

### **데이터 품질 관리**
- 중복 제거: URL 기반 자동 제거
- 피싱 유형 분류: 11가지 유형 (OpenAI 기반)
- 주기적 업데이트: GitHub Actions로 매일 자동 수집 (KST 09:00)

---

## 🤖 GitHub Actions 자동화

### **1️⃣ 백엔드 자동 배포** (`.github/workflows/deploy-backend.yml`)

**트리거:**
- `main` 브랜치에 `backend/` 폴더 변경 후 push 시 자동 실행
- 수동 실행 가능 (workflow_dispatch)

**실행 단계:**
```
1. 테스트 (pytest)
2. 린팅 (flake8, black)
3. Railway 자동 배포
4. 헬스체크 (/health)
```

**배포 환경:**
- Platform: Railway.app
- URL: https://ph-production-4b6a.up.railway.app
- 자동 롤백: 빌드 실패 시

### **2️⃣ 데이터 파이프라인** (`.github/workflows/daily-data-pipeline.yml`)

**트리거:**
- 매일 자동 실행 (UTC 00:00 = KST 09:00)
- 수동 실행 가능

**실행 단계:**
```
1. 병렬 크롤링 (5개 동시)
   ├─ 네이버 뉴스
   ├─ Google 뉴스 (국내)
   ├─ Google 뉴스 (해외)
   ├─ Reddit
   └─ Google Images

2. 데이터 전처리
   ├─ 중복 제거
   ├─ 피싱 유형 분류 (OpenAI)
   └─ 번역 (한/영)

3. 임베딩 & 업로드
   └─ Supabase 저장
```

---

## 🎯 피싱 판단 근거 (3단계 분석)

### **1단계: 규칙 기반 검사 (Rule Engine)**

**키워드 매칭 (300+ 패턴)**
```json
{
  "무단 결제": 35점,
  "계정 정지": 30점,
  "링크 클릭": 15점,
  "정보 확인": 20점,
  "긴급": 20점
}
```

**문맥 기반 점수 조정 (Context-aware Scoring)**
- **Boost Keywords**: 조합 키워드 감지 시 점수 증가
  - 예: "카카오 + 인증번호" → 65점 (단독 "카카오"는 5점)
- **Safe Patterns**: 일상 표현 감지 시 점수 감소
  - 예: "ㅋㅋ", "고마워", "밥 먹었어?" → -10~-15점

**결과:**
- 점수: 0-100점
- 매칭된 규칙 목록

---

### **2단계: 벡터 검색 (RAG - Retrieval-Augmented Generation)**

**pgvector + HNSW 인덱스 검색**
```python
# 1. 입력 메시지 → 벡터 변환
embedding = openai.embeddings.create(
    model="text-embedding-3-small",
    input=message
)

# 2. Supabase pgvector RPC로 유사한 사례 검색
# 뉴스: 네이버/구글/Reddit 전체 5,800개 검색
news_results = supabase.rpc('find_similar_phishing', {
    'query_embedding': embedding,
    'match_threshold': 0.3,  # 코사인 유사도 ≥ 0.3
    'match_count': 3          # 뉴스 상위 3개
})

# 이미지: Google Images OCR 전체 1,337개 검색
image_results = supabase.rpc('find_similar_phishing_images', {
    'query_embedding': embedding,
    'match_threshold': 0.3,
    'match_count': 2          # 이미지 상위 2개
})

# HNSW 인덱스로 전체 검색 → 밀리초 단위
# SELECT * FROM phishing_news/phishing_images
# ORDER BY embedding <=> query_embedding 
# LIMIT N

# 4. 점수 계산
score = max_similarity * 30  # 최대 30점
```

**최적화:**
- **HNSW 인덱스**: 근사 최근접 이웃(ANN) 알고리즘으로 빠른 검색
- **전체 DB 검색**: 
  - 뉴스 5,800개 전체 (네이버 + 구글 + Reddit)
  - 이미지 1,337개 전체 (Google Images OCR)
  - pgvector RPC 함수로 DB 레벨 최적화
- **정확도**: 샘플링 방식보다 훨씬 정확

**결과:**
- 유사 사례 개수 (0-5개)
- 최대 유사도 점수 (0-30점)
- 검색 시간: ~100ms

---

### **3단계: LLM 분석 (OpenAI GPT-4o-mini)**

**프롬프트 구조**
```
역할: 한국 피싱/스미싱 전문가

피싱 유형 (11가지):
- 계좌이체 요청 사기
- 무단 결제 알림 스미싱
- 택배 배송 스미싱
- 카드/계좌 정지 협박
- 대출 사기
- ...

오탐 방지 가이드:
- 일상 대화 표현 (ㅋㅋ, 고마워) → 정상
- 단순 키워드만으로 판단 금지
- 요구/유도/압박이 있을 때만 피싱

분석 요청:
메시지: "{{message}}"
유사 사례: {{similar_cases}}
```

**LLM 응답 형식**
```json
{
  "is_phishing": true,
  "confidence": 0.85,
  "risk_score": 75,
  "phishing_type": "무단 결제 알림 스미싱",
  "reasoning": "무단 결제를 주장하며 긴급 확인을 요구..."
}
```

**LLM 정상 판정 시 점수 감소**
- 확신도 90% 이상 → 점수 -70%
- 확신도 70-90% → 점수 -50%
- 확신도 70% 미만 → 점수 -30%

---

### **최종 점수 계산**

```python
final_score = (
    rule_score +          # 규칙 기반 (0-100)
    vector_score +        # 벡터 검색 (0-30)
    llm_score            # LLM 분석 (0-100)
) * llm_reduction_factor  # LLM 정상 판정 시 감소

# 위험도 분류
if final_score >= 70:   risk_level = "high"      # 높음
elif final_score >= 50: risk_level = "medium"    # 보통
elif final_score >= 30: risk_level = "low"       # 낮음
else:                   risk_level = "safe"      # 안전
```

---

## 🏗️ 시스템 아키텍처

```
┌─────────────────┐
│   사용자 입력    │ (웹/모바일)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Next.js Frontend│ (Vercel)
│  - TypeScript    │
│  - Tailwind CSS  │
│  - Capacitor     │
└────────┬────────┘
         │ HTTP Request
         ▼
┌─────────────────────────────────┐
│    FastAPI Backend (Railway)    │
│  ┌───────────────────────────┐  │
│  │  1. Rule Engine (규칙)    │  │
│  │     ├─ 키워드 매칭         │  │
│  │     └─ 문맥 기반 조정      │  │
│  └───────────────────────────┘  │
│  ┌───────────────────────────┐  │
│  │  2. Vector Search (RAG)   │  │
│  │     ├─ OpenAI Embedding   │  │
│  │     └─ Supabase pgvector  │  │
│  └───────────────────────────┘  │
│  ┌───────────────────────────┐  │
│  │  3. LLM Analysis          │  │
│  │     └─ GPT-4o-mini        │  │
│  └───────────────────────────┘  │
│  ┌───────────────────────────┐  │
│  │  4. Scorer (종합 판단)     │  │
│  └───────────────────────────┘  │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────┐
│   분석 결과      │
│ - 위험도 (0-100) │
│ - 피싱 유형      │
│ - 권장사항       │
└─────────────────┘
```

---

## 🚀 빠른 시작

### **1. 환경 설정**

```bash
# 저장소 클론
git clone https://github.com/realtheai/PH.git
cd PH

# 환경 변수 설정
cp .env.example .env
# .env 파일을 열어 API 키 입력
```

### **2. 백엔드 실행**

```bash
cd backend

# Python 의존성 설치
pip install -r requirements.txt

# 서버 실행 (포트 8888)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8888
```

### **3. 프론트엔드 실행**

```bash
cd frontend

# Node.js 의존성 설치
npm install

# 개발 서버 실행 (포트 3000)
npm run dev
```

### **4. 모바일 APK 빌드**

```bash
cd frontend

# Capacitor 동기화 + APK 빌드
npm run cap:sync
cd android
./gradlew assembleDebug

# APK 출력:
# frontend/android/app/build/outputs/apk/debug/app-debug.apk
```

---

## 🔐 환경 변수

필수 환경 변수를 `.env` 파일에 설정:

```env
# OpenAI
OPENAI_API_KEY=sk-...

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...

# Google (선택)
GOOGLE_API_KEY=AIza...
GOOGLE_SAFE_BROWSING_API_KEY=AIza...

# Frontend (production)
NEXT_PUBLIC_API_URL=https://ph-production-4b6a.up.railway.app
```

---

## 📡 API 엔드포인트

### **POST `/api/v1/analyze`**
메시지 피싱 분석

**Request:**
```json
{
  "message": "분석할 메시지"
}
```

**Response:**
```json
{
  "risk_score": 75,
  "risk_level": "high",
  "is_phishing": true,
  "phishing_type": "무단 결제 알림 스미싱",
  "phishing_probability": 85,
  "matched_rules": [
    {
      "keyword": "무단 결제",
      "score": 35,
      "description": "..."
    }
  ],
  "similar_cases_count": 3,
  "llm_analysis": {
    "is_phishing": true,
    "confidence": 0.85,
    "risk_score": 75,
    "reasoning": "..."
  },
  "recommendations": [
    "🚨 위험한 메시지입니다. 즉시 대응을 중단하세요.",
    "..."
  ]
}
```

### **GET `/health`**
서버 상태 확인

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

## 📊 성능 지표

| 항목 | 수치 |
|------|------|
| **응답 시간** | 2-4초 (LLM + 벡터 검색 포함) |
| **정확도** | ~85% (실제 피싱 사례 기준) |
| **오탐율** | ~10% (일상 대화 오인식) |
| **처리량** | 100+ req/min |
| **월 비용** | $5-10 (OpenAI API) |

---

## 🧪 테스트

### **백엔드 테스트**
```bash
cd backend

# 단위 테스트
pytest tests/ -v

# 커버리지
pytest tests/ --cov=app --cov-report=html
```

### **API 테스트**
```bash
# 피싱 메시지 (높은 위험도)
curl -X POST http://localhost:8888/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"message": "[모바일 초대] 결혼식 일시: 02/21(토) 11:00 많이 와주세요 <skm.mediaquki.com/>"}'

# 정상 메시지 (안전)
curl -X POST http://localhost:8888/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"message": "오늘 저녁 뭐 먹을까?"}'
```

---

## 🚢 배포

### **프론트엔드 (Vercel)**
1. Vercel 가입 및 GitHub 연동
2. Root Directory: `frontend`
3. Build Command: `npm run build`
4. Output Directory: `.next` (Next.js default)
5. 환경 변수 추가: `NEXT_PUBLIC_API_URL`

### **백엔드 (Railway.app)**
1. Railway 가입 및 GitHub 연동
2. Root Directory: `backend`
3. Start Command: Docker 자동 감지
4. 환경 변수 추가: `OPENAI_API_KEY`, `SUPABASE_URL`, etc.

---

## 📈 모니터링

- **헬스체크**: `GET /health`
- **백엔드 로그**: Railway Dashboard
- **프론트엔드 로그**: Vercel Dashboard
- **API 사용량**: OpenAI Usage Dashboard
- **데이터베이스**: Supabase Dashboard

---


## 📝 라이선스

MIT License

---

## 👤 작성자

- GitHub: [@realtheai](https://github.com/realtheai)
- Repository: [github.com/realtheai/PH](https://github.com/realtheai/PH)

---

## 🙏 감사의 말

- **OpenAI**: GPT-4o-mini, text-embedding-3-small
- **Supabase**: PostgreSQL + pgvector
- **Vercel**: 프론트엔드 호스팅
- **Railway**: 백엔드 호스팅
- **Google**: Safe Browsing API
- **실제 피싱 사례 데이터 제공자들**: 네이버 뉴스, Google Images/News

---

## ⚠️ 주의사항

이 시스템은 **보조 도구**로 사용되어야 하며, **100% 정확도를 보장하지 않습니다**.

의심스러운 메시지는 항상 다음 기관에 직접 확인하세요:
- 경찰청 사이버안전국: 국번없이 **182**
- 금융감독원: **1332**
- 한국인터넷진흥원(KISA): **118**

---

**🛡️ 피싱으로부터 안전한 디지털 생활을 응원합니다!**
