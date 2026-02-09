# 📰 뉴스 크롤러 가이드

## ✅ **수집 완료 현황**

### 📊 **2026-01-30 크롤링 결과**

| 출처 | 수집량 | 상태 | 파일 |
|-----|-------|------|------|
| 구글 뉴스 | **120건** | ✅ 완료 | `data/raw/news_all_20260130_144317.json` |
| 네이버 뉴스 | 0건 | ⚠️ 차단됨 | - |

---

## 🎯 **수집된 피싱 키워드 분석**

### 상위 15개 키워드
1. 피싱 (56건)
2. 보이스피싱 (37건)
3. 사칭 (24건)
4. 스미싱 (17건)
5. 개인정보 (12건)
6. 금융사기 (10건)
7. 택배 (9건)
8. 카드론 (8건)
9. 대출 (7건)
10. 메신저피싱 (6건)
11. 환급금 (5건)
12. 계좌이체 (4건)
13. 공공기관 사칭 (4건)
14. 차단 (3건)
15. 금융감독원 (3건)

---

## 📁 **크롤러 스크립트**

### 1. `scripts/crawl_google_news.py` ✅
- **기능**: 구글 뉴스 검색 및 크롤링
- **방식**: `requests` + `BeautifulSoup`
- **장점**: 빠르고 안정적
- **상태**: ✅ **작동 중**

### 2. `scripts/crawl_naver_news.py` ⚠️
- **기능**: 네이버 뉴스 검색 및 크롤링
- **방식**: `requests` + `BeautifulSoup`
- **상태**: ⚠️ **차단됨** (로봇 감지)

### 3. `scripts/crawl_naver_selenium.py` ❌
- **기능**: Selenium 기반 네이버 뉴스 크롤링
- **방식**: Selenium + ChromeDriver
- **상태**: ❌ **WSL 미지원** (GUI 필요)

### 4. `scripts/main_news_crawler.py` ✅
- **기능**: 통합 크롤러 (네이버 + 구글)
- **상태**: ✅ **작동 중** (구글만)

---

## 🚀 **사용 방법**

### 📦 **의존성 설치**
```bash
conda activate phishingapp
pip install requests beautifulsoup4 lxml
```

### 🔍 **1. 구글 뉴스 크롤링 (추천)**
```bash
python scripts/crawl_google_news.py
```

**예상 출력**:
- 키워드당 20~30건
- 총 120~300건 수집
- JSON 파일 저장

### 🔄 **2. 통합 크롤러 실행**
```bash
python scripts/main_news_crawler.py
```

**결과**:
- 네이버 + 구글 통합
- 중복 제거
- `data/raw/news_all_YYYYMMDD_HHMMSS.json` 저장

---

## 📊 **수집 데이터 포맷**

```json
{
  "source": "google_news",
  "keyword": "피싱 주의보",
  "title": "\"검찰입니다\"…다 알면서 또 속는 '복고풍 피싱' 주의보",
  "url": "https://www.news1.kr/local/sejong-chungbuk/6055293",
  "content": "최근 검찰이나 금융감독원 직원을 사칭한 보이스피싱이...",
  "press": "뉴스1",
  "date": "1일 전",
  "extracted_keywords": ["피싱", "보이스피싱", "사칭"],
  "crawled_at": "2026-01-30T14:42:34.908723"
}
```

---

## 🎯 **수집 키워드 목록**

### 한국어 키워드 (12개)
1. 피싱 주의보
2. 스미싱 사례
3. 보이스피싱 피해
4. 금융사기 수법
5. 메신저피싱
6. 계좌이체 사기
7. 개인정보 탈취
8. 공공기관 사칭
9. 택배 스미싱
10. 카드론 피싱
11. 환급금 사기
12. 금융감독원 피싱

---

## ⚠️ **현재 이슈**

### 1. **네이버 뉴스 차단**
- **문제**: `requests` 방식 차단
- **원인**: 로봇 감지 (User-Agent, Rate Limit)
- **해결**:
  - ✅ 구글 뉴스 활용 (현재 전략)
  - ⏳ Selenium (GUI 환경 필요)
  - ⏳ Playwright MCP 활용

### 2. **WSL 환경 제약**
- **문제**: Selenium Chrome 미작동
- **원인**: GUI 미지원 (headless Chrome 오류)
- **해결**: 
  - ✅ 구글 뉴스로 대체
  - ⏳ Windows 환경에서 실행

---

## 📈 **성과**

### ✅ **현재까지 수집된 데이터**

| 출처 | 건수 | 파일 크기 | 상태 |
|-----|------|---------|------|
| 구글 뉴스 | 120건 | ~50KB | ✅ 완료 |
| GitHub (Voice_phising_KR) | 1,200건 | 1.6MB | ✅ 다운로드 |
| GitHub (KOR_phishing) | 52,590건 | 4.9MB | ✅ 다운로드 |
| Kaggle (234KB) | 적음 | 234KB | ✅ 다운로드 |
| Kaggle (144GB) | 대량 | 144GB | 🔄 진행중 |

### 📊 **총 데이터 현황**
- **실제 크롤링**: 120건 (뉴스)
- **GitHub 데이터**: 53,790건
- **예상 최종**: 54,000+ 건 🔥

---

## 💡 **다음 단계**

### 1. **데이터 전처리**
- 뉴스 기사 본문 추출 (URL 접속)
- 텍스트 정제 (HTML 제거)
- 피싱 유형 분류

### 2. **데이터 증강**
- GitHub 데이터 + 뉴스 병합
- 중복 제거
- 라벨링

### 3. **Vector DB 구축**
- 임베딩 생성
- Qdrant/Chroma 저장
- RAG 시스템 구축

---

## 🔧 **커스터마이징**

### 키워드 추가
`scripts/main_news_crawler.py`:
```python
keywords_kr = [
    '새로운 키워드1',
    '새로운 키워드2',
    # ...
]
```

### 수집량 조정
```python
crawler.run(
    keywords=keywords,
    max_pages_per_keyword=10  # 페이지 수 증가
)
```

---

## 📞 **문의**

크롤러 관련 문제는 이슈를 등록하거나 로그를 확인하세요.

```bash
# 로그 확인
tail -f data/logs/crawler.log
```
