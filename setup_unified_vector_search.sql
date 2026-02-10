-- ============================================================
-- REAL_CASE 통합 검색 함수 (뉴스 + 이미지)
-- 
-- ⚠️ 사전 작업 필수:
-- migrate_category_to_classification.sql 먼저 실행하여
-- category → classification 통합 필요!
-- ============================================================

-- 0. 기존 함수 삭제 (반환 타입 변경을 위해 필요)
DROP FUNCTION IF EXISTS find_similar_phishing(vector, double precision, integer);
DROP FUNCTION IF EXISTS find_similar_phishing(vector, float, integer);

-- 1. 뉴스와 이미지를 통합 검색하는 함수
CREATE OR REPLACE FUNCTION find_similar_phishing(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.5,
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id bigint,
    source_type text,
    title text,
    content text,
    source varchar(50),
    phishing_type varchar(50),
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- statement timeout 설정 (2분)
    SET LOCAL statement_timeout = '120s';
    
    RETURN QUERY
    -- 뉴스에서 검색 (NEWS + REAL_CASE)
    SELECT 
        n.id,
        'news'::text as source_type,
        n.title,
        COALESCE(n.translated_content, n.content) as content,
        n.source,
        n.phishing_type,
        (1 - (n.embedding <=> query_embedding))::float as similarity
    FROM phishing_news n
    WHERE n.embedding IS NOT NULL
        AND n.classification IN ('REAL_CASE', 'NEWS')
        AND (1 - (n.embedding <=> query_embedding)) > match_threshold
    
    UNION ALL
    
    -- 이미지에서 검색 (NEWS + REAL_CASE)
    SELECT 
        i.id,
        'image'::text as source_type,
        NULL::text as title,
        COALESCE(i.translated_content, i.translated_text, i.ocr_text) as content,
        i.source,
        i.phishing_type,
        (1 - (i.embedding <=> query_embedding))::float as similarity
    FROM phishing_images i
    WHERE i.embedding IS NOT NULL
        AND i.classification IN ('REAL_CASE', 'NEWS')
        AND (1 - (i.embedding <=> query_embedding)) > match_threshold
    
    ORDER BY similarity DESC
    LIMIT match_count;
END;
$$;

-- 코멘트
COMMENT ON FUNCTION find_similar_phishing IS '뉴스와 이미지를 통합하여 유사한 피싱 사례 검색 (classification 사용)';

-- ============================================================
-- 통계 확인
-- ============================================================

-- REAL_CASE + NEWS 임베딩 통계
SELECT 
    '뉴스 (REAL_CASE + NEWS)' as type,
    COUNT(*) as total,
    COUNT(embedding) as embedded,
    ROUND(COUNT(embedding)::numeric / NULLIF(COUNT(*), 0)::numeric * 100, 2) as percentage
FROM phishing_news
WHERE classification IN ('REAL_CASE', 'NEWS')

UNION ALL

SELECT 
    '이미지 (REAL_CASE + NEWS)' as type,
    COUNT(*) as total,
    COUNT(embedding) as embedded,
    ROUND(COUNT(embedding)::numeric / NULLIF(COUNT(*), 0)::numeric * 100, 2) as percentage
FROM phishing_images
WHERE classification IN ('REAL_CASE', 'NEWS');
