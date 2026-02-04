-- ============================================================
-- Phishingapp Supabase 데이터베이스 스키마
-- 생성일: 2026-02-01
-- ============================================================

-- ============================================================
-- 1. phishing_news 테이블 (뉴스/텍스트 데이터)
-- ============================================================

CREATE TABLE IF NOT EXISTS phishing_news (
    -- 기본 키
    id BIGSERIAL PRIMARY KEY,
    
    -- 데이터 소스
    source VARCHAR(50) NOT NULL,           -- 'naver', 'google', 'reddit', 'intl'
    
    -- 콘텐츠
    title TEXT NOT NULL,
    content TEXT,
    url TEXT UNIQUE,                        -- 중복 방지
    
    -- 분류
    category VARCHAR(20),                   -- 'REAL_CASE', 'NEWS', 'NOISE'
    phishing_type VARCHAR(50),              -- '가족사칭', '기관사칭', '택배사칭' etc.
    
    -- 번역 (영어 데이터인 경우)
    original_language VARCHAR(10),          -- 'ko', 'en'
    translated_content TEXT,                -- 번역된 내용
    
    -- 메타데이터
    keywords TEXT[],                        -- 추출된 키워드 배열
    content_length INTEGER,
    
    -- 타임스탬프
    published_at TIMESTAMPTZ,               -- 원본 게시 시간
    crawled_at TIMESTAMPTZ,                 -- 크롤링 시간
    processed_at TIMESTAMPTZ DEFAULT NOW(), -- 정제 시간
    created_at TIMESTAMPTZ DEFAULT NOW()    -- DB 저장 시간
);

-- 인덱스 생성 (검색 성능 향상)
CREATE INDEX IF NOT EXISTS idx_phishing_news_source ON phishing_news(source);
CREATE INDEX IF NOT EXISTS idx_phishing_news_category ON phishing_news(category);
CREATE INDEX IF NOT EXISTS idx_phishing_news_published ON phishing_news(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_phishing_news_url ON phishing_news(url);

-- 코멘트 추가
COMMENT ON TABLE phishing_news IS '피싱 뉴스 및 텍스트 데이터';
COMMENT ON COLUMN phishing_news.source IS '데이터 소스: naver, google, reddit, intl';
COMMENT ON COLUMN phishing_news.category IS '분류: REAL_CASE(실제사례), NEWS(뉴스), NOISE(무관)';


-- ============================================================
-- 2. phishing_images 테이블 (이미지 데이터)
-- ============================================================

CREATE TABLE IF NOT EXISTS phishing_images (
    -- 기본 키
    id BIGSERIAL PRIMARY KEY,
    
    -- 이미지 정보
    query VARCHAR(100),                     -- 검색 키워드
    image_url TEXT,                         -- 원본 이미지 URL
    local_path TEXT,                        -- 로컬 저장 경로
    
    -- OCR 결과
    ocr_text TEXT,                          -- OCR로 추출한 원문
    translated_text TEXT,                   -- 번역된 텍스트
    language VARCHAR(10),                   -- 'ko', 'en'
    
    -- 메타데이터
    text_length INTEGER,                    -- 텍스트 길이
    
    -- 타임스탬프
    crawled_at TIMESTAMPTZ,                 -- 크롤링 시간
    processed_at TIMESTAMPTZ DEFAULT NOW(), -- OCR 처리 시간
    created_at TIMESTAMPTZ DEFAULT NOW()    -- DB 저장 시간
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_phishing_images_query ON phishing_images(query);
CREATE INDEX IF NOT EXISTS idx_phishing_images_language ON phishing_images(language);

-- 코멘트 추가
COMMENT ON TABLE phishing_images IS '피싱 이미지 및 OCR 데이터';
COMMENT ON COLUMN phishing_images.ocr_text IS 'EasyOCR로 추출한 원문';


-- ============================================================
-- 3. phishing_stats 테이블 (일별 통계)
-- ============================================================

CREATE TABLE IF NOT EXISTS phishing_stats (
    -- 기본 키
    id BIGSERIAL PRIMARY KEY,
    
    -- 날짜 (UNIQUE - 하루에 하나의 통계만)
    stat_date DATE NOT NULL UNIQUE,
    
    -- 데이터 수집 통계
    naver_count INTEGER DEFAULT 0,          -- 네이버 수집 건수
    google_count INTEGER DEFAULT 0,         -- 구글 수집 건수
    reddit_count INTEGER DEFAULT 0,         -- Reddit 수집 건수
    intl_count INTEGER DEFAULT 0,           -- 해외 뉴스 수집 건수
    images_count INTEGER DEFAULT 0,         -- 이미지 수집 건수
    
    -- 분류 통계
    real_case_count INTEGER DEFAULT 0,      -- 실제 사례 건수
    news_count INTEGER DEFAULT 0,           -- 일반 뉴스 건수
    noise_count INTEGER DEFAULT 0,          -- 무관 데이터 건수
    
    -- 타임스탬프
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_phishing_stats_date ON phishing_stats(stat_date DESC);

-- 코멘트 추가
COMMENT ON TABLE phishing_stats IS '일별 데이터 수집 및 분류 통계';


-- ============================================================
-- RLS (Row Level Security) 정책 설정 (선택사항)
-- ============================================================

-- 모든 테이블에 대해 읽기 허용
ALTER TABLE phishing_news ENABLE ROW LEVEL SECURITY;
ALTER TABLE phishing_images ENABLE ROW LEVEL SECURITY;
ALTER TABLE phishing_stats ENABLE ROW LEVEL SECURITY;

-- 읽기 정책 (모든 사용자 허용)
CREATE POLICY "Allow read access to all users" ON phishing_news
    FOR SELECT USING (true);

CREATE POLICY "Allow read access to all users" ON phishing_images
    FOR SELECT USING (true);

CREATE POLICY "Allow read access to all users" ON phishing_stats
    FOR SELECT USING (true);

-- 쓰기 정책 (인증된 사용자만 허용)
CREATE POLICY "Allow authenticated insert" ON phishing_news
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated insert" ON phishing_images
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated insert/update" ON phishing_stats
    FOR ALL WITH CHECK (auth.role() = 'authenticated');


-- ============================================================
-- 초기 데이터 확인 쿼리
-- ============================================================

-- 테이블 생성 확인
SELECT table_name, table_type 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name LIKE 'phishing%'
ORDER BY table_name;

-- 각 테이블 레코드 수 확인
SELECT 
    'phishing_news' as table_name, 
    COUNT(*) as count 
FROM phishing_news
UNION ALL
SELECT 
    'phishing_images' as table_name, 
    COUNT(*) as count 
FROM phishing_images
UNION ALL
SELECT 
    'phishing_stats' as table_name, 
    COUNT(*) as count 
FROM phishing_stats;
