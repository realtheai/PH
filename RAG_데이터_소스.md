# RAG 데이터 수집 소스 - 한국 피싱/스미싱 데이터

## 🎯 목표
한국인 전용 피싱 예방 서비스를 위한 **RAG (Retrieval-Augmented Generation)** 시스템에 넣을 **실시간 피싱/스미싱 데이터** 수집

---

## 📊 주요 데이터 소스 (확인 완료)

### 1. ✅ **KISA 불법스팸대응센터** (https://spam.kisa.or.kr/)

**데이터 유형:**
- 스팸신고 현황 (월별 통계)
- 실제 피싱/스미싱 사례
- 주의 권고 공지사항
- 홍보자료 (피싱 유형별 안내)

**수집 가능한 컨텐츠:**

#### A. 공지사항 (피싱 사례)
- ✅ "[주의] 이커머스(쿠팡) 해킹 피해 악용 스미싱·피싱 주의 권고" (2025-12-09)
- ✅ "[주의] \"민생회복 소비쿠폰 지급\" 사칭 피싱 주의 권고" (2025-07-10)
- ✅ "[주의] SKT 해킹 이슈를 악용한 피싱 주의 권고"
- ✅ "불법스팸대응센터 및 수사기관 사칭 문자 주의" (2025-01-06)

#### B. 스팸신고 현황 (통계 데이터)
- 2025년 12월 대량문자사업자별 스팸신고 현황
- 2025년 11월 대량문자사업자별 스팸신고 현황
- 월별 스팸 유통 현황 보고서

#### C. 자료실 (보고서)
- 25년 상반기 스팸 유통현황 발표
- 2024년 하반기 스팸 유통현황 및 수신량 조사 결과
- 통계정보보고서 스팸수신량

#### D. 홍보자료 (교육 컨텐츠)
- AI 기반 악성 메시지 차단 기능 안내
- 연말을 노리는 스팸문자 주의
- KISA 사칭 피싱메일 주의

**수집 방법:**
```python
# 웹 크롤링 (BeautifulSoup + Selenium)
https://spam.kisa.or.kr/spam/main.do
https://spam.kisa.or.kr/spam/sub61.do  # 공지사항
https://spam.kisa.or.kr/spam/sub63.do  # 자료실
https://spam.kisa.or.kr/spam/sub64.do  # 홍보자료
```

---

### 2. ✅ **KISA 보호나라** (https://www.boho.or.kr/)

**데이터 유형:**
- 보안공지 (최신 위협 정보)
- 보고서/가이드
- 사이버 위협 동향

**수집 가능한 컨텐츠:**
- 최신 보안 위협 정보
- 피싱 관련 가이드 문서
- 사이버 위협 동향 분석 보고서

---

### 3. **Dacon 대회 참가자 코드 공유**

**링크:** https://dacon.io/competitions/official/236666/codeshare

**데이터 유형:**
- 다른 참가자들이 공유한 코드
- 데이터 전처리 방법
- 모델링 접근법

---

## 🌐 해외 공개 데이터셋 (보완용)

### 1. **Kaggle**
- [SMS Spam Collection Dataset](https://www.kaggle.com/datasets/uciml/sms-spam-collection-dataset)
- [Phishing Website Detection](https://www.kaggle.com/datasets/shashwatwork/web-page-phishing-detection-dataset)
- [Email Spam Classification](https://www.kaggle.com/datasets/balaka18/email-spam-classification-dataset-csv)

### 2. **UCI Machine Learning Repository**
- [SMS Spam Collection](https://archive.ics.uci.edu/ml/datasets/SMS+Spam+Collection)
- [Phishing Websites](https://archive.ics.uci.edu/ml/datasets/Phishing+Websites)

### 3. **GitHub 오픈소스**
- 피싱 탐지 프로젝트에서 공유된 데이터셋
- 한국어 스미싱 샘플 데이터

---

## 🛠️ RAG 데이터 수집 자동화 전략

### Phase 1: 웹 크롤링
```python
# 대상 사이트
sources = [
    "https://spam.kisa.or.kr/",  # KISA 불법스팸대응센터
    "https://www.boho.or.kr/",   # KISA 보호나라
]

# 수집할 데이터
- 공지사항 (최근 100개)
- 주의 권고 (전체)
- 피싱 사례 (상세 내용)
- 통계 보고서 (PDF -> 텍스트 변환)
```

### Phase 2: 데이터 전처리
```python
# 1. HTML -> Markdown 변환
# 2. PDF -> 텍스트 추출 (PyPDF2 / pdfplumber)
# 3. 중복 제거
# 4. 청크 분할 (Chunk Size: 500-1000 tokens)
```

### Phase 3: Embedding 및 Vector DB 저장
```python
# Embedding Model
- KoBERT / KoELECTRA (한국어 특화)
- OpenAI text-embedding-ada-002 (다국어)

# Vector Database
- Qdrant / Pinecone / Chroma
- Supabase Vector (PostgreSQL + pgvector)
```

---

## 📁 RAG 데이터 구조

### 메타데이터 스키마
```json
{
  "id": "unique_id",
  "source": "KISA 불법스팸대응센터",
  "url": "https://spam.kisa.or.kr/...",
  "title": "쿠팡 사칭 피싱 주의 권고",
  "date": "2025-12-09",
  "category": "스미싱",
  "type": "기관사칭",
  "keywords": ["쿠팡", "택배", "링크", "개인정보"],
  "content": "...",
  "embedding": [0.1, 0.2, ...]
}
```

---

## 🔄 실시간 업데이트 전략

### 1. 정기 크롤링
```python
# 매일 오전 9시 실행
- KISA 공지사항 체크
- 새로운 피싱 사례 자동 수집
- Vector DB 자동 업데이트
```

### 2. RSS 피드 활용
```python
# KISA 보호나라 RSS
https://www.boho.or.kr/rss/rssboard.do
```

### 3. API 연동 (가능 시)
```python
# KISA OpenAPI (확인 필요)
# 실시간 스팸 신고 데이터 수신
```

---

## 📊 예상 데이터 규모

### 초기 수집 목표
- **KISA 공지사항**: 500~1,000건
- **주의 권고**: 100~200건
- **보고서/가이드**: 50~100건
- **Kaggle 데이터셋**: 5,000~10,000건

### 총 예상 데이터
- **텍스트 청크**: 10,000~20,000개
- **Vector Embeddings**: 10,000~20,000개

---

## 🚀 다음 단계 작업

### 1. 크롤링 스크립트 작성
```bash
# 파일 구조
/scripts
  ├── crawl_kisa_spam.py      # KISA 불법스팸대응센터 크롤러
  ├── crawl_kisa_boho.py      # KISA 보호나라 크롤러
  ├── process_data.py         # 데이터 전처리
  ├── create_embeddings.py    # Embedding 생성
  └── upload_to_vectordb.py   # Vector DB 업로드
```

### 2. RAG 시스템 구축
```bash
/rag_system
  ├── config/
  │   └── vector_db_config.yaml
  ├── embeddings/
  │   └── embedding_model.py
  ├── retriever/
  │   └── semantic_search.py
  └── generator/
      └── llm_integration.py
```

### 3. API 개발
```bash
/api
  ├── routes/
  │   └── phishing_check.py   # 피싱 판별 API
  ├── models/
  │   └── rag_model.py
  └── main.py
```

---

## 💡 RAG 활용 시나리오

### 사용자 질문 예시
```
Q: "쿠팡에서 택배 확인하라는 문자가 왔는데 피싱인가요?"
→ RAG가 KISA 데이터에서 "쿠팡 사칭 피싱 사례" 검색
→ 유사 사례 + 대응 방법 제공

Q: "은행에서 보안등급 업그레이드하라는 문자가 왔어요"
→ RAG가 "금융기관 사칭 스미싱" 사례 검색
→ 경고 + 신고 방법 안내
```

---

## 📝 참고 링크

- [KISA 불법스팸대응센터](https://spam.kisa.or.kr/)
- [KISA 보호나라](https://www.boho.or.kr/)
- [Dacon 피싱 대회](https://dacon.io/competitions/official/236666/overview/description)
- [Kaggle SMS Spam Dataset](https://www.kaggle.com/datasets/uciml/sms-spam-collection-dataset)

---

## ✅ 결론

RAG에 넣을 데이터는 **KISA 불법스팸대응센터**와 **KISA 보호나라**에서 **실시간 한국 피싱/스미싱 사례**를 크롤링하여 수집하는 것이 가장 효과적입니다.

### 핵심 장점:
1. ✅ **실시간 최신 데이터** (매일 업데이트)
2. ✅ **한국어 피싱 사례** (한국인 타겟)
3. ✅ **공공기관 공식 데이터** (신뢰성 높음)
4. ✅ **다양한 피싱 유형** (기관사칭, 택배사칭, 금융사칭 등)
5. ✅ **대응 방법 포함** (사용자 교육 가능)
