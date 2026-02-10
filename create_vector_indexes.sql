-- ============================================================
-- 벡터 검색 인덱스 생성 (HNSW - 빠르고 정확)
-- ============================================================

-- 기존 인덱스 확인
SELECT 
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
  AND (tablename = 'phishing_news' OR tablename = 'phishing_images')
  AND indexname LIKE '%embedding%';

-- ============================================================
-- 1. 뉴스 테이블 벡터 인덱스
-- ============================================================

-- 기존 인덱스 삭제 (있다면)
DROP INDEX IF EXISTS phishing_news_embedding_idx;

-- HNSW 인덱스 생성 (가장 빠르고 정확)
CREATE INDEX phishing_news_embedding_idx 
ON phishing_news 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 인덱스 생성 진행률 확인
SELECT 
    phase,
    round(100.0 * blocks_done / nullif(blocks_total, 0), 1) AS "% complete",
    blocks_total,
    blocks_done
FROM pg_stat_progress_create_index
WHERE relid = 'phishing_news'::regclass;

-- ============================================================
-- 2. 이미지 테이블 벡터 인덱스
-- ============================================================

-- 기존 인덱스 삭제 (있다면)
DROP INDEX IF EXISTS phishing_images_embedding_idx;

-- HNSW 인덱스 생성
CREATE INDEX phishing_images_embedding_idx 
ON phishing_images 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- ============================================================
-- 3. 인덱스 생성 확인
-- ============================================================

SELECT 
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
  AND (tablename = 'phishing_news' OR tablename = 'phishing_images')
  AND indexname LIKE '%embedding%';

-- ============================================================
-- 4. 인덱스 통계 확인
-- ============================================================

SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as "index_scans",
    idx_tup_read as "tuples_read",
    idx_tup_fetch as "tuples_fetched"
FROM pg_stat_user_indexes
WHERE indexname LIKE '%embedding%'
ORDER BY idx_scan DESC;

-- ============================================================
-- 참고: HNSW vs IVFFlat
-- ============================================================
-- HNSW (Hierarchical Navigable Small World):
--   - 장점: 매우 빠름, 높은 정확도
--   - 단점: 인덱스 크기가 큼, 빌드 시간 김
--   - 추천: 대부분의 경우 (현재 사용)
--
-- IVFFlat:
--   - 장점: 빌드 빠름, 작은 인덱스 크기
--   - 단점: 정확도 낮음, 느림
--   - 사용법: CREATE INDEX ... USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
-- ============================================================
