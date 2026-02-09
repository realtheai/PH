# 데이터 정제 → DB 저장 자동화 설계

## 📊 전체 흐름

```
┌─────────────────────────────────────────┐
│  1. 크롤링 (매일/주간)                   │
│     ├─ Naver API (매일)                 │
│     ├─ Google News (매일)               │
│     ├─ Reddit (주 2회)                  │
│     ├─ 해외 뉴스 (주 1회)               │
│     └─ Google Images (주 1회)           │
│     ↓                                   │
│  JSON 파일 저장 (data/raw/daily/)       │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  2. 데이터 정제 (자동 트리거)            │
│     ├─ OCR (이미지 → 텍스트)            │
│     ├─ 번역 (영어 → 한국어)             │
│     ├─ 분류 (REAL_CASE/NEWS/NOISE)     │
│     └─ 중복 제거 (임베딩 유사도)        │
│     ↓                                   │
│  JSON 파일 저장 (data/processed/)       │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  3. Supabase DB 저장                    │
│     ├─ phishing_news (뉴스 데이터)      │
│     ├─ phishing_images (이미지 데이터)  │
│     └─ phishing_stats (통계)            │
└─────────────────────────────────────────┘
```

---

## 🗄️ Supabase 테이블 스키마

### **1. phishing_news** (뉴스/텍스트 데이터)
```sql
CREATE TABLE phishing_news (
    id BIGSERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,           -- 'naver', 'google', 'reddit', 'intl'
    title TEXT NOT NULL,
    content TEXT,
    url TEXT UNIQUE,
    
    -- 분류
    category VARCHAR(20),                   -- 'REAL_CASE', 'NEWS', 'NOISE'
    phishing_type VARCHAR(50),              -- '가족사칭', '기관사칭', etc.
    
    -- 번역 (영어 데이터인 경우)
    original_language VARCHAR(10),          -- 'ko', 'en'
    translated_content TEXT,                -- 번역된 내용
    
    -- 메타데이터
    keywords TEXT[],                        -- 추출된 키워드
    content_length INTEGER,
    
    -- 타임스탬프
    published_at TIMESTAMPTZ,
    crawled_at TIMESTAMPTZ,
    processed_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- 인덱스
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_phishing_news_source ON phishing_news(source);
CREATE INDEX idx_phishing_news_category ON phishing_news(category);
CREATE INDEX idx_phishing_news_published ON phishing_news(published_at DESC);
```

### **2. phishing_images** (이미지 데이터)
```sql
CREATE TABLE phishing_images (
    id BIGSERIAL PRIMARY KEY,
    query VARCHAR(100),                     -- 검색 키워드
    image_url TEXT,
    local_path TEXT,
    
    -- OCR 결과
    ocr_text TEXT,
    translated_text TEXT,
    language VARCHAR(10),                   -- 'ko', 'en'
    
    -- 메타데이터
    text_length INTEGER,
    
    -- 타임스탬프
    crawled_at TIMESTAMPTZ,
    processed_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_phishing_images_query ON phishing_images(query);
```

### **3. phishing_stats** (통계 데이터)
```sql
CREATE TABLE phishing_stats (
    id BIGSERIAL PRIMARY KEY,
    stat_date DATE NOT NULL UNIQUE,
    
    -- 데이터 수집
    naver_count INTEGER DEFAULT 0,
    google_count INTEGER DEFAULT 0,
    reddit_count INTEGER DEFAULT 0,
    intl_count INTEGER DEFAULT 0,
    images_count INTEGER DEFAULT 0,
    
    -- 분류 통계
    real_case_count INTEGER DEFAULT 0,
    news_count INTEGER DEFAULT 0,
    noise_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 🔄 자동화 프로세스

### **Phase 1: 크롤링 (GitHub Actions)**
```yaml
# .github/workflows/daily-crawl.yml
name: Daily Data Crawl

on:
  schedule:
    - cron: '0 0 * * *'  # 매일 00:00 (UTC)

jobs:
  crawl:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run Naver Crawler
        run: python scripts/daily_naver.py
      
      - name: Run Google Crawler
        run: python scripts/daily_google.py
      
      - name: Process & Upload to DB
        run: python scripts/auto_process_and_upload.py
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_ANON_KEY: ${{ secrets.SUPABASE_ANON_KEY }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
```

### **Phase 2: 데이터 정제 + DB 저장**
스크립트: `scripts/auto_process_and_upload.py`

```python
1. 최신 JSON 파일 읽기 (data/raw/daily/)
2. 데이터 정제:
   - 영어 텍스트 번역
   - Gemini로 분류 (REAL_CASE/NEWS/NOISE)
   - 중복 제거
3. Supabase에 INSERT
4. 통계 업데이트
```

---

## 🎯 다음 단계

1. **Supabase 테이블 생성** (SQL 실행)
2. **자동화 스크립트 작성** (`auto_process_and_upload.py`)
3. **GitHub Actions 워크플로우 설정**
4. **테스트 실행**

---

## ⚡ 핵심 장점

✅ **완전 자동화**: 크롤링 → 정제 → DB 저장
✅ **중복 방지**: URL 기반 UNIQUE 제약
✅ **확장 가능**: 새 데이터 소스 추가 쉬움
✅ **통계 관리**: 일별 데이터 수집 현황 추적
✅ **비용 0원**: GitHub Actions 무료 (2,000분/월)
