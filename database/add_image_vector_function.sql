-- ============================================================
-- phishing_images 테이블용 벡터 검색 함수 추가
-- ============================================================

-- 이미지 벡터 검색 함수
CREATE OR REPLACE FUNCTION find_similar_phishing_images(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.3,
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id bigint,
    ocr_text text,
    translated_text text,
    translated_content text,
    source varchar(50),
    phishing_type varchar(50),
    classification varchar(20),
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        phishing_images.id,
        phishing_images.ocr_text,
        phishing_images.translated_text,
        phishing_images.translated_content,
        phishing_images.source,
        phishing_images.phishing_type,
        phishing_images.classification,
        1 - (phishing_images.embedding <=> query_embedding) as similarity
    FROM phishing_images
    WHERE phishing_images.embedding IS NOT NULL
        AND 1 - (phishing_images.embedding <=> query_embedding) > match_threshold
    ORDER BY phishing_images.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- 코멘트 추가
COMMENT ON FUNCTION find_similar_phishing_images IS '이미지 임베딩 벡터로 유사한 피싱 이미지 검색 (코사인 유사도, HNSW 인덱스)';

-- ============================================================
-- 테스트 쿼리
-- ============================================================

-- 샘플 이미지 임베딩으로 테스트
-- SELECT * FROM find_similar_phishing_images(
--     (SELECT embedding FROM phishing_images WHERE embedding IS NOT NULL LIMIT 1)::vector(1536),
--     0.3,
--     5
-- );
