-- ============================================================
-- Supabase pgvector 확장 + embedding 컬럼 추가
-- ============================================================

-- 1. pgvector 확장 활성화
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. phishing_news 테이블에 embedding 컬럼 추가
ALTER TABLE phishing_news 
ADD COLUMN IF NOT EXISTS embedding vector(1536);

-- 3. HNSW 인덱스 생성 (빠른 유사도 검색)
CREATE INDEX IF NOT EXISTS idx_phishing_news_embedding 
ON phishing_news 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 4. 유사도 검색 함수
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

-- 5. 임베딩 통계 뷰
CREATE OR REPLACE VIEW phishing_embedding_stats AS
SELECT 
    COUNT(*) as total_records,
    COUNT(embedding) as embedded_records,
    COUNT(*) - COUNT(embedding) as pending_records,
    ROUND(COUNT(embedding)::numeric / NULLIF(COUNT(*), 0)::numeric * 100, 2) as completion_percentage
FROM phishing_news;

-- 6. 확인 쿼리
SELECT 
    'vector 확장' as check_item,
    CASE WHEN EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector') 
        THEN '✅ 활성화됨' 
        ELSE '❌ 없음' 
    END as status
UNION ALL
SELECT 
    'embedding 컬럼' as check_item,
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'phishing_news' AND column_name = 'embedding'
    ) THEN '✅ 존재함' 
      ELSE '❌ 없음' 
    END as status
UNION ALL
SELECT 
    'find_similar_phishing 함수' as check_item,
    CASE WHEN EXISTS (
        SELECT 1 FROM pg_proc WHERE proname = 'find_similar_phishing'
    ) THEN '✅ 존재함' 
      ELSE '❌ 없음' 
    END as status;

-- 7. 통계 확인
SELECT * FROM phishing_embedding_stats;
