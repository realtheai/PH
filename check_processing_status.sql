-- ============================================================
-- 데이터 처리 상태 확인 쿼리
-- Supabase SQL Editor에서 실행하세요
-- ============================================================

-- 1. phishing_news 처리 상태
SELECT 
    '📰 phishing_news' as table_name,
    COUNT(*) as total,
    COUNT(classification) as classified,
    COUNT(phishing_type) as typed,
    COUNT(embedding) as embedded,
    COUNT(translated_content) as translated,
    ROUND(COUNT(classification)::numeric / NULLIF(COUNT(*), 0)::numeric * 100, 1) as classification_pct,
    ROUND(COUNT(embedding)::numeric / NULLIF(COUNT(*), 0)::numeric * 100, 1) as embedding_pct
FROM phishing_news;

-- 2. phishing_images 처리 상태
SELECT 
    '🖼️ phishing_images' as table_name,
    COUNT(*) as total,
    COUNT(ocr_text) as ocr_done,
    COUNT(classification) as classified,
    COUNT(phishing_type) as typed,
    COUNT(embedding) as embedded,
    COUNT(translated_content) as translated,
    ROUND(COUNT(ocr_text)::numeric / NULLIF(COUNT(*), 0)::numeric * 100, 1) as ocr_pct,
    ROUND(COUNT(classification)::numeric / NULLIF(COUNT(*), 0)::numeric * 100, 1) as classification_pct,
    ROUND(COUNT(embedding)::numeric / NULLIF(COUNT(*), 0)::numeric * 100, 1) as embedding_pct
FROM phishing_images;

-- 3. phishing_news 분류별 통계
SELECT 
    'phishing_news 분류' as category,
    classification,
    COUNT(*) as count
FROM phishing_news
WHERE classification IS NOT NULL
GROUP BY classification
ORDER BY count DESC;

-- 4. phishing_images 분류별 통계
SELECT 
    'phishing_images 분류' as category,
    classification,
    COUNT(*) as count
FROM phishing_images
WHERE classification IS NOT NULL
GROUP BY classification
ORDER BY count DESC;

-- 5. phishing_type 통계 (뉴스)
SELECT 
    'phishing_news 타입' as category,
    phishing_type,
    COUNT(*) as count
FROM phishing_news
WHERE phishing_type IS NOT NULL
GROUP BY phishing_type
ORDER BY count DESC
LIMIT 10;

-- 6. 최근 데이터 샘플 (뉴스)
SELECT 
    id,
    source,
    title,
    classification,
    phishing_type,
    embedding IS NOT NULL as has_embedding,
    created_at
FROM phishing_news
ORDER BY created_at DESC
LIMIT 5;

-- 7. 최근 데이터 샘플 (이미지)
SELECT 
    id,
    query,
    source,
    classification,
    phishing_type,
    ocr_text IS NOT NULL as has_ocr,
    embedding IS NOT NULL as has_embedding,
    created_at
FROM phishing_images
ORDER BY created_at DESC
LIMIT 5;
