-- ============================================================
-- Phishingapp Vector Search 확장 스키마
-- pgvector를 사용한 의미 기반 검색
-- ============================================================

-- pgvector 확장 활성화
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================
-- phishing_news 테이블에 embedding 컬럼 추가
-- ============================================================

-- embedding 컬럼 추가 (1536 차원 - OpenAI/Gemini embedding)
ALTER TABLE phishing_news 
ADD COLUMN IF NOT EXISTS embedding vector(1536);

-- embedding 인덱스 생성 (HNSW - 빠른 유사도 검색)
CREATE INDEX IF NOT EXISTS idx_phishing_news_embedding 
ON phishing_news 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 코멘트 추가
COMMENT ON COLUMN phishing_news.embedding IS '텍스트 임베딩 벡터 (1536차원)';

-- ============================================================
-- 유사도 검색 함수
-- ============================================================

-- 1. 코사인 유사도로 유사 문서 찾기
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

-- 2. 텍스트로 직접 검색 (프론트엔드용)
CREATE OR REPLACE FUNCTION search_phishing_by_text(
    search_text text,
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
DECLARE
    query_embedding vector(1536);
BEGIN
    -- 여기서는 이미 생성된 embedding을 사용
    -- 실제로는 백엔드에서 embedding을 생성하고 이 함수에 전달
    RETURN QUERY
    SELECT * FROM find_similar_phishing(query_embedding, match_threshold, match_count);
END;
$$;

-- 코멘트 추가
COMMENT ON FUNCTION find_similar_phishing IS '임베딩 벡터로 유사한 피싱 사례 검색 (코사인 유사도)';
COMMENT ON FUNCTION search_phishing_by_text IS '텍스트로 유사한 피싱 사례 검색';

-- ============================================================
-- 통계 뷰 (임베딩 처리 상태)
-- ============================================================

CREATE OR REPLACE VIEW phishing_embedding_stats AS
SELECT 
    COUNT(*) as total_records,
    COUNT(embedding) as embedded_records,
    COUNT(*) - COUNT(embedding) as pending_records,
    ROUND(COUNT(embedding)::numeric / COUNT(*)::numeric * 100, 2) as completion_percentage
FROM phishing_news;

-- 코멘트
COMMENT ON VIEW phishing_embedding_stats IS '임베딩 처리 진행률 통계';

-- ============================================================
-- 확인 쿼리
-- ============================================================

-- 임베딩 통계 확인
SELECT * FROM phishing_embedding_stats;

-- 샘플 유사도 검색 테스트
-- (실제 사용 시 백엔드에서 embedding 생성 후 전달)
-- SELECT * FROM find_similar_phishing(
--     (SELECT embedding FROM phishing_news WHERE embedding IS NOT NULL LIMIT 1)::vector(1536),
--     0.7,
--     5
-- );
