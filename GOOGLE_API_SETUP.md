# 🔑 Google Custom Search API 설정 가이드

## 📋 **현재 상태**

```
✅ GOOGLE_API_KEY: 설정 완료
⚠️ GOOGLE_CSE_ID: 설정 필요
```

---

## 🚀 **Custom Search Engine ID 생성 방법**

### **1단계: Programmable Search Engine 페이지 접속**

```
https://programmablesearchengine.google.com/
```

### **2단계: 새 검색 엔진 생성**

1. **"Add"** 버튼 클릭
2. 다음 정보 입력:
   ```
   Name: Phishing News Search
   What to search: Search the entire web
   ```
3. **"Create"** 클릭

### **3단계: Search Engine ID 복사**

1. 생성된 검색 엔진 클릭
2. **"Setup"** → **"Basics"** 탭
3. **"Search engine ID"** 복사
   ```
   예시: 01234567890abcdef:ghijklmnop
   ```

### **4단계: `.env` 파일 업데이트**

```bash
GOOGLE_CSE_ID=여기에_복사한_ID_붙여넣기
```

---

## ⚙️ **추가 설정 (권장)**

### **뉴스 검색 최적화**

1. **"Setup"** → **"Basics"**
2. **"Sites to search"** 섹션에서 "Search the entire web" 선택
3. **"Refinements"** → "News" 추가

### **언어 설정**

1. **"Setup"** → **"Basics"**
2. **"Language"** → **"Korean"** 선택

---

## 📊 **API 할당량**

### **무료 티어**
```
✅ 100 쿼리/일
✅ 최대 10개 결과/쿼리
━━━━━━━━━━━━━━━━━━━
총: 1,000개 결과/일
```

### **유료 티어** (필요 시)
```
💰 $5/1,000 쿼리
✅ 무제한 쿼리
✅ 최대 10개 결과/쿼리
```

---

## 🔥 **하이브리드 방식 사용**

### **자동 전환**
```python
if GOOGLE_CSE_ID 설정됨:
    → Custom Search API 사용 (빠름, 안정적)
else:
    → HTML 파싱 사용 (느림, 무제한)
```

### **크롤링 전략**
```
1단계: API로 URL 목록 수집 (빠름)
2단계: newspaper3k로 전체 본문 추출 (정확)
━━━━━━━━━━━━━━━━━━━━━━━━━━
결과: 속도 10배 + 전체 본문 확보 ✅
```

---

## ✅ **설정 확인**

### **테스트 실행**

```bash
python scripts/test_google_content.py
```

### **예상 출력**

```
🔑 Google Custom Search API 사용
🔍 구글 Custom Search API 뉴스 검색: '피싱 사례'
   📄 API 응답: 10개
      [1] 본문 추출 중... ✅ (2094자)
      [2] 본문 추출 중... ✅ (1682자)
```

---

## 🔧 **트러블슈팅**

### **문제 1: "API key not valid"**

```bash
# 해결: API 키 확인
1. https://console.cloud.google.com/apis/credentials
2. API 키 재생성
3. .env 파일 업데이트
```

### **문제 2: "CSE ID not found"**

```bash
# 해결: CSE ID 확인
1. https://programmablesearchengine.google.com/
2. Search engine ID 재확인
3. .env 파일 업데이트
```

### **문제 3: "Quota exceeded"**

```bash
# 해결: 할당량 초과
✅ 24시간 대기 (무료 티어)
✅ 유료 플랜 전환
✅ HTML 파싱 방식으로 자동 전환
```

---

## 📝 **다음 단계**

1. ✅ CSE ID 생성 및 설정
2. ✅ 테스트 실행 확인
3. ✅ 전체 크롤링 시작

```bash
# 전체 크롤링 (28개 키워드)
python scripts/crawl_google_news.py
```

---

## 💡 **참고 링크**

- [Programmable Search Engine](https://programmablesearchengine.google.com/)
- [Custom Search JSON API](https://developers.google.com/custom-search/v1/overview)
- [API Console](https://console.cloud.google.com/apis/credentials)
