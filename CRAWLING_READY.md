# 📦 피싱 데이터 수집 준비 완료

## ✅ **완료된 작업**

### **1. 크롤러 업데이트 (날짜 범위: 2025-02-01 ~ 2026-01-31)**

```
✅ scripts/crawl_naver_api.py          (28개 키워드)
✅ scripts/crawl_google_news.py        (28개 키워드)
✅ scripts/crawl_reddit.py             (12개 서브레딧)
✅ scripts/crawl_international_news.py (12개 쿼리)
✅ scripts/crawl_google_images.py      (20개 키워드)
```

### **2. newspaper3k 본문 추출 적용**

```
✅ 네이버 API: 전체 본문 추출 (평균 1,500자)
✅ 구글 뉴스: 전체 본문 추출 (평균 1,800자)
```

### **3. JSON 저장 형식**

```
data/raw/
  ├── naver_api_2025-02-01_to_2026-01-31.json
  ├── google_news_2025-02-01_to_2026-01-31.json
  ├── reddit_2025-02-01_to_2026-01-31.json
  ├── international_news_2025-02-01_to_2026-01-31.json
  └── google_images_2025-02-01_to_2026-01-31.json

data/images/
  └── (피싱 관련 이미지 파일들)
```

---

## 🚀 **크롤링 실행 방법**

### **방법 1: 개별 실행**

```bash
# 1. 네이버 API (약 25분)
python scripts/crawl_naver_api.py

# 2. 구글 뉴스 (약 15분)
python scripts/crawl_google_news.py

# 3. Reddit (약 5분)
python scripts/crawl_reddit.py

# 4. 해외 뉴스 (약 3분)
python scripts/crawl_international_news.py

# 5. 구글 이미지 (약 10분)
python scripts/crawl_google_images.py
```

### **방법 2: 통합 실행 (추천) ✅**

```bash
python scripts/run_all_crawlers.py
```

---

## 📊 **예상 수집량**

| 소스 | 키워드/서브레딧 | 예상 수집량 | 소요 시간 |
|------|----------------|------------|----------|
| 네이버 API | 28개 | 2,800건 | 약 25분 |
| 구글 뉴스 | 28개 | 1,400건 | 약 15분 |
| Reddit | 12개 | 500건 | 약 5분 |
| 해외 뉴스 | 12개 | 360건 | 약 3분 |
| 구글 이미지 | 20개 | 1,000개 | 약 10분 |
| **합계** | **100개** | **6,060건** | **약 60분** |

---

## 💾 **예상 데이터 크기**

```
네이버:      2,800건 × 1,500자 = 4.2MB (JSON)
구글:        1,400건 × 1,800자 = 2.5MB (JSON)
Reddit:        500건 × 500자  = 0.3MB (JSON)
해외 뉴스:     360건 × 800자  = 0.3MB (JSON)
이미지:      1,000개 × 200KB = 200MB
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
총계:                         약 207MB
```

---

## 🔧 **주요 기능**

### **1. 날짜 필터링**
```python
# 네이버 API는 자동으로 날짜 필터링
start_date = '2025-02-01'
end_date = '2026-01-31'
```

### **2. 중복 제거**
```python
# URL 기준 자동 중복 제거
unique_results = {}
for result in all_results:
    url = result['url']
    if url not in unique_results:
        unique_results[url] = result
```

### **3. 전체 본문 추출**
```python
# newspaper3k로 전체 기사 본문 추출
full_content = fetch_full_content(url)
```

---

## 📝 **데이터 구조**

### **뉴스 데이터 (JSON)**
```json
{
  "source": "naver_api",
  "keyword": "피싱 주의보",
  "title": "제목",
  "url": "https://...",
  "content": "전체 본문 (1,500자)",
  "content_length": 1500,
  "date": "2025-12-01",
  "extracted_keywords": ["피싱", "사기", "금융"],
  "crawled_at": "2026-01-31T12:00:00"
}
```

### **이미지 데이터 (JSON)**
```json
{
  "query": "스미싱 문자 사례",
  "image_url": "https://...",
  "local_path": "data/images/스미싱_문자_사례_1.jpg",
  "filename": "스미싱_문자_사례_1.jpg",
  "crawled_at": "2026-01-31T12:00:00"
}
```

---

## 🎯 **다음 단계**

### **1단계: 데이터 수집 (오늘)**
```bash
python scripts/run_all_crawlers.py
```

### **2단계: 데이터 검증 (내일)**
```bash
# 수집된 데이터 확인
ls -lh data/raw/

# 샘플 데이터 확인
head -20 data/raw/naver_api_2025-02-01_to_2026-01-31.json
```

### **3단계: 전처리 (다음)**
```python
# 1. 중복 제거
# 2. 불필요한 데이터 필터링
# 3. 텍스트 정제
# 4. 통합 JSON 생성
```

### **4단계: Vector DB 구축**
```python
# 1. Qdrant 설치 및 설정
# 2. 임베딩 생성 (OpenAI/Ko-SBERT)
# 3. 벡터 저장
# 4. 검색 테스트
```

---

## ⚠️ **주의사항**

### **1. API 제한**
```
네이버 API: 25,000 call/일 (충분)
```

### **2. 크롤링 속도**
```
본문 추출: 0.5초/건 (newspaper3k)
→ 과부하 방지 위한 적절한 딜레이
```

### **3. 에러 처리**
```
본문 추출 실패 시: API description 사용
URL 접근 실패 시: 스킵하고 계속 진행
```

---

## 🔥 **즉시 시작 가능!**

```bash
# 전체 크롤링 시작
cd /home/realtheai/phishingapp
python scripts/run_all_crawlers.py
```

**예상 소요 시간: 약 60분**
**예상 데이터: 6,060건 + 1,000개 이미지**

---

## 📞 **문제 발생 시**

### **1. newspaper3k 설치 오류**
```bash
pip install newspaper3k
```

### **2. 네이버 API 오류**
```bash
# .env 파일 확인
cat .env

# API 키 재확인
```

### **3. 디스크 공간 부족**
```bash
# 최소 1GB 이상 확보
df -h
```

---

**준비 완료! 🚀**
