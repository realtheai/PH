-- ============================================================
-- RLS 정책 수정 - API 접근 허용
-- ============================================================

-- 기존 정책 삭제
DROP POLICY IF EXISTS "Allow read access to all users" ON phishing_news;
DROP POLICY IF EXISTS "Allow authenticated insert" ON phishing_news;
DROP POLICY IF EXISTS "Allow read access to all users" ON phishing_images;
DROP POLICY IF EXISTS "Allow authenticated insert" ON phishing_images;

-- 새로운 정책 생성 (읽기/쓰기 모두 허용)
CREATE POLICY "Allow all access" ON phishing_news
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all access" ON phishing_images
    FOR ALL USING (true) WITH CHECK (true);

-- 확인
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd
FROM pg_policies
WHERE tablename IN ('phishing_news', 'phishing_images')
ORDER BY tablename, policyname;
