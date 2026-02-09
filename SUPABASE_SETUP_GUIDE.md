# Supabase Vector Search 설정 가이드

## 🎯 목표

피싱체커 앱에서 2,712건의 과거 피싱 데이터를 활용하여 의미 기반 유사도 검색을 구현합니다.

---

## 📋 Step 1: Supabase Dashboard에서 SQL 실행

### 1. Supabase Dashboard 열기

https://app.supabase.com 접속 → 프로젝트 선택 (`wqepkzgehbqrtkrzkimn`)

### 2. SQL Editor로 이동

왼쪽 메뉴에서 **SQL Editor** 클릭

### 3. 기본 테이블 생성

**New Query** 클릭 → 아래 SQL 복사 붙여넣기 → **Run** 클릭

```sql
-- ============================================================
-- 1. phishing_news 테이블 생성
-- ============================================================

CREATE TABLE IF NOT EXISTS phishing_news (
    id BIGSERIAL PRIMARY KEY,
    
    -- 데이터 소스
    source VARCHAR(50) NOT NULL,
    
    -- 콘텐츠
    title TEXT NOT NULL,
    content TEXT,
    url TEXT UNIQUE,
    
    -- 분류
    category VARCHAR(20),
    phishing_type VARCHAR(50),
    
    -- 번역
    original_language VARCHAR(10),
    translated_content TEXT,
    
    -- 메타데이터
    keywords TEXT[],
    content_length INTEGER,
    
    -- 타임스탬프
    published_at TIMESTAMPTZ,
    crawled_at TIMESTAMPTZ,
    processed_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_phishing_news_source ON phishing_news(source);
CREATE INDEX IF NOT EXISTS idx_phishing_news_category ON phishing_news(category);
CREATE INDEX IF NOT EXISTS idx_phishing_news_published ON phishing_news(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_phishing_news_url ON phishing_news(url);

-- ============================================================
-- 2. phishing_images 테이블 생성
-- ============================================================

CREATE TABLE IF NOT EXISTS phishing_images (
    id BIGSERIAL PRIMARY KEY,
    
    query VARCHAR(100),
    image_url TEXT,
    local_path TEXT,
    
    ocr_text TEXT,
    translated_text TEXT,
    language VARCHAR(10),
    
    text_length INTEGER,
    
    crawled_at TIMESTAMPTZ,
    processed_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_phishing_images_query ON phishing_images(query);
CREATE INDEX IF NOT EXISTS idx_phishing_images_language ON phishing_images(language);

-- ============================================================
-- 3. phishing_stats 테이블 생성
-- ============================================================

CREATE TABLE IF NOT EXISTS phishing_stats (
    id BIGSERIAL PRIMARY KEY,
    
    stat_date DATE NOT NULL UNIQUE,
    
    naver_count INTEGER DEFAULT 0,
    google_count INTEGER DEFAULT 0,
    reddit_count INTEGER DEFAULT 0,
    intl_count INTEGER DEFAULT 0,
    images_count INTEGER DEFAULT 0,
    
    real_case_count INTEGER DEFAULT 0,
    news_count INTEGER DEFAULT 0,
    noise_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_phishing_stats_date ON phishing_stats(stat_date DESC);
```

### 4. pgvector 확장 활성화

**New Query** 클릭 → 아래 SQL 실행

```sql
-- ============================================================
-- pgvector 확장 활성화
-- ============================================================

CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================
-- embedding 컬럼 추가
-- ============================================================

ALTER TABLE phishing_news 
ADD COLUMN IF NOT EXISTS embedding vector(1536);

-- HNSW 인덱스 생성 (빠른 유사도 검색)
CREATE INDEX IF NOT EXISTS idx_phishing_news_embedding 
ON phishing_news 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- ============================================================
-- 유사도 검색 함수
-- ============================================================

CREATE OR REPLACE FUNCTION find_similar_phishing(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id bigint,
    title text,
    content text,
    source varchar(50),
    phishing_type varchar(50),
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        phishing_news.id,
        phishing_news.title,
        phishing_news.content,
        phishing_news.source,
        phishing_news.phishing_type,
        1 - (phishing_news.embedding <=> query_embedding) as similarity
    FROM phishing_news
    WHERE phishing_news.embedding IS NOT NULL
        AND 1 - (phishing_news.embedding <=> query_embedding) > match_threshold
    ORDER BY phishing_news.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- ============================================================
-- 통계 뷰
-- ============================================================

CREATE OR REPLACE VIEW phishing_embedding_stats AS
SELECT 
    COUNT(*) as total_records,
    COUNT(embedding) as embedded_records,
    COUNT(*) - COUNT(embedding) as pending_records,
    ROUND(COUNT(embedding)::numeric / NULLIF(COUNT(*), 0)::numeric * 100, 2) as completion_percentage
FROM phishing_news;
```

---

## 📊 Step 2: 설정 확인

### 확인 쿼리 실행

```sql
-- 1. 테이블 목록 확인
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name LIKE 'phishing%'
ORDER BY table_name;

-- 2. pgvector 확장 확인
SELECT * FROM pg_extension WHERE extname = 'vector';

-- 3. embedding 컬럼 확인
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'phishing_news' 
  AND column_name = 'embedding';

-- 4. 임베딩 통계 확인
SELECT * FROM phishing_embedding_stats;
```

---

## ✅ 예상 결과

```
테이블 목록:
- phishing_news ✅
- phishing_images ✅
- phishing_stats ✅
- phishing_embedding_stats (View) ✅

pgvector 확장:
- extname: vector ✅

embedding 컬럼:
- column_name: embedding
- data_type: vector(1536) ✅

임베딩 통계:
- total_records: 0 (처음에는 0)
- embedded_records: 0
- pending_records: 0
- completion_percentage: 0.00
```

---

## 🚀 다음 단계

Supabase 설정이 완료되면:

1. 백엔드 의존성 업데이트
2. 2,712건 데이터 임베딩 생성
3. Supabase에 업로드
4. Vector Search API 테스트

---

**준비되면 다음 명령어를 실행하세요:**

```bash
cd /home/realtheai/phishingapp
python scripts/create_embeddings_and_upload.py
```
