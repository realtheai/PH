# 🚀 Vector Search 설정 가이드 (빠른 시작)

## 현재 상태 ✅

- [x] Supabase 기본 테이블 생성 완료
- [x] Supabase 키 설정 완료 (.env)
- [x] 2,712건 Raw 데이터 수집 완료
- [ ] **pgvector 확장 추가 필요** ⬅️ 지금 할 일!
- [ ] 데이터 정제 + 임베딩 생성
- [ ] Supabase 업로드

---

## 📋 Step 1: Supabase에서 pgvector 설정 (2분)

### 1-1. Supabase Dashboard 열기

```
https://app.supabase.com/project/wqepkzgehbqrtkrzkimn/editor
```

### 1-2. SQL Editor에서 실행

왼쪽 메뉴 **SQL Editor** 클릭 → **New Query** 클릭

### 1-3. SQL 복사 & 실행

아래 SQL을 복사해서 붙여넣고 **Run** 클릭:

```sql
-- pgvector 확장 활성화
CREATE EXTENSION IF NOT EXISTS vector;

-- embedding 컬럼 추가
ALTER TABLE phishing_news 
ADD COLUMN IF NOT EXISTS embedding vector(1536);

-- HNSW 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_phishing_news_embedding 
ON phishing_news 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 유사도 검색 함수
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

-- 통계 뷰
CREATE OR REPLACE VIEW phishing_embedding_stats AS
SELECT 
    COUNT(*) as total_records,
    COUNT(embedding) as embedded_records,
    COUNT(*) - COUNT(embedding) as pending_records,
    ROUND(COUNT(embedding)::numeric / NULLIF(COUNT(*), 0)::numeric * 100, 2) as completion_percentage
FROM phishing_news;
```

**또는** 파일 사용:

```bash
# setup_vector.sql 파일 내용을 복사해서 SQL Editor에 붙여넣기
cat setup_vector.sql
```

### 1-4. 확인

SQL Editor에서 확인 쿼리 실행:

```sql
-- 1. pgvector 확장 확인
SELECT * FROM pg_extension WHERE extname = 'vector';

-- 2. embedding 컬럼 확인
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'phishing_news' AND column_name = 'embedding';

-- 3. 함수 확인
SELECT proname FROM pg_proc WHERE proname = 'find_similar_phishing';

-- 4. 통계 확인
SELECT * FROM phishing_embedding_stats;
```

**예상 결과:**
```
✅ vector 확장: 존재
✅ embedding 컬럼: vector(1536)
✅ find_similar_phishing 함수: 존재
✅ 통계: total_records = 0
```

---

## 📊 Step 2: 데이터 정제 + 임베딩 생성 (30-40분)

Supabase 설정이 완료되면 바로 실행:

```bash
cd /home/realtheai/phishingapp
python scripts/process_and_embed.py
```

**프로세스:**
1. 2,712건 Raw 데이터 로드
2. Gemini로 분류 (REAL_CASE/NEWS/NOISE)
3. NOISE 제거 → 약 1,500건 선별
4. 임베딩 생성 (1536차원 벡터)
5. Supabase 업로드

**예상 소요 시간:**
- 분류: ~15분
- 임베딩: ~15분
- 업로드: ~5분
- **총: 35분**

---

## 🔧 Step 3: 백엔드 의존성 업데이트

```bash
cd backend
pip install google-generativeai==0.3.2 numpy==1.26.0
```

---

## 🚀 Step 4: 백엔드 재시작

```bash
# 기존 서버 종료
pkill -f "uvicorn"

# 재시작
cd backend
uvicorn app.main:app --reload --port 8888
```

---

## 🧪 Step 5: 테스트

```bash
curl -X POST http://localhost:8888/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "message": "긴급! 국세청입니다. 세금 환급이 있습니다. 링크를 클릭하세요: http://fake-tax.com"
  }'
```

**예상 결과:**

```json
{
  "risk_score": 95,
  "risk_level": "critical",
  "is_phishing": true,
  "phishing_type": "기관사칭",
  "similar_cases_count": 3,
  "db_similarity_score": 45,
  "recommendations": [
    "📊 DB에서 유사한 피싱 사례 3건이 발견되었습니다.",
    "🚨 즉시 삭제하고 링크를 절대 클릭하지 마세요.",
    "..."
  ]
}
```

---

## 📈 완성 후 효과

### Before (Rule-Based만)
```
키워드 매칭 → 60점 → "위험"
```

### After (Rule-Based + Vector Search)
```
키워드 매칭 60점 
+ DB 유사 사례 45점
= 105점 → 100점 (critical)
+ "유사 사례 3건 발견"
```

---

## 💡 빠른 시작 체크리스트

- [ ] 1. Supabase SQL 실행 (2분)
- [ ] 2. `python scripts/process_and_embed.py` (35분)
- [ ] 3. 백엔드 의존성 설치 (1분)
- [ ] 4. 백엔드 재시작 (1분)
- [ ] 5. 테스트 (1분)

**총 소요 시간: 약 40분**

---

## 🆘 문제 해결

### pgvector 확장 오류
```
ERROR: extension "vector" is not available
```
→ Supabase에서 pgvector는 기본 제공됩니다. Dashboard에서 실행하세요.

### 임베딩 생성 실패
```
API 키 로테이션 사용 (6개 키)
각 키당 15 RPM 제한 = 총 90 RPM
```

### 업로드 실패
```
배치 크기 30건씩 자동 처리
실패 시 개별 재시도
```

---

**준비되셨나요? Supabase SQL 실행 후 진행하세요!** 🚀
