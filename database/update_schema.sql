-- ============================================================
-- Supabase 스키마 업데이트 (스크립트 호환성)
-- ============================================================

-- 1. phishing_news 테이블 업데이트
-- category -> classification 컬럼 이름 변경
ALTER TABLE phishing_news 
RENAME COLUMN category TO classification;

-- 인덱스도 업데이트
DROP INDEX IF EXISTS idx_phishing_news_category;
CREATE INDEX IF NOT EXISTS idx_phishing_news_classification 
ON phishing_news(classification);

COMMENT ON COLUMN phishing_news.classification IS '분류: REAL_CASE(실제사례), NEWS(뉴스), NOISE(무관)';


-- 2. phishing_images 테이블 업데이트
-- 필요한 컬럼 추가
ALTER TABLE phishing_images 
ADD COLUMN IF NOT EXISTS source VARCHAR(50),
ADD COLUMN IF NOT EXISTS classification VARCHAR(20),
ADD COLUMN IF NOT EXISTS phishing_type VARCHAR(50),
ADD COLUMN IF NOT EXISTS translated_content TEXT,
ADD COLUMN IF NOT EXISTS embedding vector(1536);

-- 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_phishing_images_source 
ON phishing_images(source);

CREATE INDEX IF NOT EXISTS idx_phishing_images_classification 
ON phishing_images(classification);

CREATE INDEX IF NOT EXISTS idx_phishing_images_embedding 
ON phishing_images 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

COMMENT ON COLUMN phishing_images.source IS '데이터 소스: google_images, reddit';
COMMENT ON COLUMN phishing_images.classification IS '분류: REAL_CASE(실제사례), NEWS(뉴스), NOISE(무관)';
COMMENT ON COLUMN phishing_images.phishing_type IS '피싱 유형: 가족사칭, 기관사칭, 택배사칭 등';


-- 3. phishing_reddit 테이블 생성
CREATE TABLE IF NOT EXISTS phishing_reddit (
    -- 기본 키
    id BIGSERIAL PRIMARY KEY,
    
    -- 데이터 소스
    source VARCHAR(50) DEFAULT 'reddit',
    
    -- 콘텐츠
    title TEXT NOT NULL,
    content TEXT,
    url TEXT UNIQUE,
    subreddit VARCHAR(100),
    author VARCHAR(100),
    score INTEGER,
    
    -- 분류
    classification VARCHAR(20),
    phishing_type VARCHAR(50),
    
    -- 번역
    original_language VARCHAR(10) DEFAULT 'en',
    translated_content TEXT,
    
    -- 메타데이터
    keywords TEXT[],
    content_length INTEGER,
    
    -- 타임스탬프
    published_at TIMESTAMPTZ,
    crawled_at TIMESTAMPTZ,
    processed_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- 임베딩
    embedding vector(1536)
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_phishing_reddit_subreddit 
ON phishing_reddit(subreddit);

CREATE INDEX IF NOT EXISTS idx_phishing_reddit_classification 
ON phishing_reddit(classification);

CREATE INDEX IF NOT EXISTS idx_phishing_reddit_published 
ON phishing_reddit(published_at DESC);

CREATE INDEX IF NOT EXISTS idx_phishing_reddit_url 
ON phishing_reddit(url);

CREATE INDEX IF NOT EXISTS idx_phishing_reddit_embedding 
ON phishing_reddit 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

COMMENT ON TABLE phishing_reddit IS 'Reddit 피싱 관련 게시물';
COMMENT ON COLUMN phishing_reddit.classification IS '분류: REAL_CASE(실제사례), NEWS(뉴스), NOISE(무관)';


-- 4. RLS 정책 추가 (phishing_reddit)
ALTER TABLE phishing_reddit ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow read access to all users" ON phishing_reddit
    FOR SELECT USING (true);

CREATE POLICY "Allow authenticated insert" ON phishing_reddit
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');


-- 5. 확인 쿼리
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'public' 
  AND table_name IN ('phishing_news', 'phishing_images', 'phishing_reddit')
  AND column_name IN ('classification', 'phishing_type', 'embedding', 'source', 'translated_content')
ORDER BY table_name, column_name;
