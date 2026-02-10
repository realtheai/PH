-- ============================================================
-- category 데이터를 classification으로 통합
-- ============================================================

-- 1. 기존 category 데이터를 classification으로 복사
UPDATE phishing_news 
SET classification = category 
WHERE category IS NOT NULL 
  AND classification IS NULL;

-- 2. 통합 결과 확인
SELECT 
    'category 분포' as type,
    category,
    COUNT(*) as count
FROM phishing_news
GROUP BY category
ORDER BY count DESC;

SELECT 
    'classification 분포 (통합 후)' as type,
    classification,
    COUNT(*) as count
FROM phishing_news
GROUP BY classification
ORDER BY count DESC;

-- 3. REAL_CASE + NEWS 카운트 확인
SELECT 
    '검색 대상' as type,
    COUNT(*) as total,
    COUNT(embedding) as embedded,
    ROUND(COUNT(embedding)::numeric / NULLIF(COUNT(*), 0)::numeric * 100, 2) as percentage
FROM phishing_news
WHERE classification IN ('REAL_CASE', 'NEWS');
