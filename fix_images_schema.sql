-- ============================================================
-- Supabase 스키마 업데이트 (실제 상태 기반)
-- ============================================================

-- 1. phishing_news: category -> classification 변경하지 않음
--    (이미 category로 사용 중이므로, 스크립트를 category에 맞춤)

-- 2. phishing_images: 필요한 컬럼 추가
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

-- 확인
SELECT 
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'phishing_images'
  AND column_name IN ('classification', 'phishing_type', 'embedding', 'source', 'translated_content')
ORDER BY column_name;
