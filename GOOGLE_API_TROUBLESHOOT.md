# 🔧 Google Custom Search API 활성화 가이드

## ❌ **현재 문제**

```
403 Client Error: Forbidden
```

➡️ **원인**: Custom Search API가 Google Cloud Console에서 활성화되지 않음

---

## ✅ **해결 방법 (5분 소요)**

### **1단계: Google Cloud Console 접속**

```
https://console.cloud.google.com/
```

### **2단계: 프로젝트 선택/생성**

1. 상단 프로젝트 드롭다운 클릭
2. 기존 프로젝트 선택 또는 **"새 프로젝트"** 생성
   ```
   프로젝트 이름: Phishing Detection
   ```

### **3단계: Custom Search API 활성화**

1. 검색창에 **"Custom Search API"** 입력
2. **"Custom Search API"** 클릭
3. **"사용 설정"** 버튼 클릭 ✅

또는 직접 링크:
```
https://console.cloud.google.com/apis/library/customsearch.googleapis.com
```

### **4단계: API 키 재생성 (권장)**

1. **"사용자 인증 정보"** 메뉴 이동
   ```
   https://console.cloud.google.com/apis/credentials
   ```
2. **"+ 사용자 인증 정보 만들기"** → **"API 키"** 클릭
3. 생성된 API 키 복사
4. `.env` 파일 업데이트:
   ```bash
   GOOGLE_API_KEY=새로_생성한_API_키
   ```

### **5단계: API 키 제한 설정 (보안)**

1. 생성된 API 키 옆 **연필 아이콘** 클릭
2. **"API 제한사항"** 섹션
3. **"키 제한"** 선택
4. **"Custom Search API"** 체크 ✅
5. **"저장"** 클릭

---

## 🔄 **대안: HTML 파싱 모드로 계속 진행**

API 설정이 번거로우면, **HTML 파싱 모드**로 바로 크롤링 가능합니다:

```bash
# .env에서 GOOGLE_CSE_ID 주석 처리
# GOOGLE_CSE_ID=5624236524d9141d0
```

➡️ 자동으로 HTML 파싱 모드로 전환됩니다!

---

## 📊 **두 모드 비교**

| 항목 | API 모드 | HTML 파싱 모드 |
|-----|----------|----------------|
| 설정 | API 활성화 필요 | 설정 불필요 ✅ |
| 속도 | ⚡ 매우 빠름 | 보통 |
| 안정성 | ✅ 매우 높음 | ⚠️ HTML 변경 시 깨짐 |
| 제한 | 100건/일 (무료) | 무제한 ✅ |
| 본문 | ✅ 전체 본문 | ✅ 전체 본문 |

---

## 🚀 **추천 방안**

### **방안 1: API 활성화 (5분) 🔥**
```bash
# 장점: 빠르고 안정적
1. Custom Search API 활성화
2. 테스트 재실행
```

### **방안 2: HTML 파싱 모드 (즉시) ✅**
```bash
# .env 수정
# GOOGLE_CSE_ID=5624236524d9141d0

# 바로 크롤링 시작
python scripts/crawl_google_news.py
```

---

## 💡 **권장 사항**

**즉시 데이터 수집이 급하다면** → HTML 파싱 모드 사용 ✅
**장기적으로 사용할 계획이라면** → API 활성화 🔥

어떤 방법으로 진행하시겠습니까?
