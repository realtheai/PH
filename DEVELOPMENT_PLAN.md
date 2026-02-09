# 🎯 Phishingapp 전체 개발 계획 & 순서

## 📊 현재 상황 (2026-02-01)

### ✅ 완료된 것
```
1. PRD 작성 완료
2. 프론트엔드 UI (Stitch) - 9개 화면 완성
3. 데이터 수집:
   - 1년치 데이터: 3,142건 + 400개 이미지
   - Daily 크롤링 스크립트 5개 준비
4. API 키 설정:
   - Google Safe Browsing ✅
   - Gemini API ✅
   - Supabase ✅
5. DB 스키마 설계 완료
```

### ⏳ 진행 필요
```
1. 데이터 정제 파이프라인
2. Supabase 테이블 생성
3. 백엔드 API (FastAPI)
4. 프론트엔드 통합
5. 모바일 빌드
6. Phase 2 (백그라운드 감지)
```

---

## 🚀 개발 순서 (우선순위)

### **📍 Stage 1: 데이터 인프라 구축** ⏰ 3-4시간
**목표**: 데이터 수집 → 정제 → DB 저장 자동화

#### **1.1 Supabase 테이블 생성** (30분)
```sql
- phishing_news 테이블
- phishing_images 테이블
- phishing_stats 테이블
```
**산출물**: Supabase에 3개 테이블 생성 완료

#### **1.2 데이터 정제 파이프라인 완성** (1-2시간)
```python
- 이미지 OCR (EasyOCR)
- 텍스트 번역 (Gemini)
- 콘텐츠 분류 (Gemini)
- 중복 제거
```
**산출물**: `scripts/process_all_data.py` 완성

#### **1.3 DB 업로드 테스트** (30분)
```python
- 1년치 데이터 → Supabase 업로드
- 데이터 무결성 검증
```
**산출물**: Supabase에 3,000+ 건 저장 완료

#### **1.4 자동화 스크립트 통합** (1시간)
```python
- 크롤링 → 정제 → DB 자동 연결
- GitHub Actions 워크플로우 설정
```
**산출물**: 완전 자동화 파이프라인

---

### **📍 Stage 2: 백엔드 API 개발** ⏰ 4-5시간
**목표**: 피싱 분석 API 구축

#### **2.1 프로젝트 구조 생성** (30분)
```
backend/
├── app/
│   ├── main.py
│   ├── api/v1/
│   ├── core/
│   └── storage/
```
**산출물**: FastAPI 프로젝트 뼈대

#### **2.2 룰 엔진 개발** (2시간)
```python
- 키워드 매칭 (기관사칭, 긴급성, 금전요구)
- 점수 계산 로직 (0-100)
- 위험도 판정 (HIGH/MEDIUM/LOW)
```
**산출물**: `core/rule_engine.py`

#### **2.3 URL 체커 통합** (1시간)
```python
- Google Safe Browsing API 호출
- 단축 URL 확장
- 도메인 유사도 체크
```
**산출물**: `core/url_checker.py`

#### **2.4 API 엔드포인트** (1시간)
```python
POST /api/v1/analyze
  - 메시지 분석
  - 룰 엔진 + URL 체크
  - 결과 반환

GET /api/v1/health
  - 헬스체크
```
**산출물**: FastAPI 서버 작동

#### **2.5 Supabase 연결** (30분)
```python
- 분석 결과 저장
- 통계 조회
```
**산출물**: 백엔드 ↔ DB 연동 완료

---

### **📍 Stage 3: 프론트엔드 통합** ⏰ 3-4시간
**목표**: Stitch UI → Next.js 변환

#### **3.1 Next.js 프로젝트 생성** (30분)
```bash
npx create-next-app@latest frontend
- App Router
- Tailwind CSS
- TypeScript
```
**산출물**: Next.js 프로젝트 생성

#### **3.2 Stitch → Next.js 변환** (2시간)
```javascript
- 9개 화면 컴포넌트화
- Tailwind 스타일 유지
- 라우팅 설정
```
**산출물**: 9개 페이지 완성

#### **3.3 API 연동** (1시간)
```javascript
- fetch('/api/v1/analyze')
- Zustand 상태 관리
- 로딩/에러 처리
```
**산출물**: 프론트 ↔ 백엔드 연동

#### **3.4 로컬 내역 저장** (30분)
```javascript
- LocalStorage persist
- 검사 내역 페이지
```
**산출물**: 전체 UI 작동

---

### **📍 Stage 4: 모바일 빌드 (Phase 1 완성)** ⏰ 2-3시간
**목표**: Share Intent → 앱 검사

#### **4.1 Capacitor 설정** (30분)
```bash
npm install @capacitor/core @capacitor/cli
npx cap init
npx cap add android
```
**산출물**: Capacitor 프로젝트

#### **4.2 Android Share Intent** (1-2시간)
```kotlin
ShareReceiverActivity.kt
- ACTION_SEND 수신
- 텍스트 추출
- WebView로 전달
```
**산출물**: Share 기능 작동

#### **4.3 APK 빌드 & 테스트** (30분)
```bash
npx cap sync
./gradlew assembleDebug
```
**산출물**: **Phase 1 MVP 완성** ✅

---

### **📍 Stage 5: Phase 2 구현 (백그라운드 감지)** ⏰ 6-8시간
**목표**: 자동 피싱 감지

#### **5.1 Accessibility Service** (2-3시간)
```kotlin
- PhishingAccessibilityService.kt
- 텍스트 변경 이벤트 감지
- 카톡/문자 앱 필터링
```
**산출물**: 백그라운드 감지 작동

#### **5.2 온디바이스 룰 엔진** (2시간)
```kotlin
- RuleEngineLocal.kt
- 경량 키워드 매칭
- URL 추출 및 체크
```
**산출물**: 로컬 분석 작동

#### **5.3 알림 시스템** (1-2시간)
```kotlin
- Heads-up 알림
- 오버레이 경고
- 상세 화면 이동
```
**산출물**: 경고 시스템 완성

#### **5.4 권한 관리 & 설정 UI** (1시간)
```kotlin
- Accessibility 권한 요청
- 보호 모드 ON/OFF
- 대상 앱 선택
```
**산출물**: **Phase 2 완성** ✅

---

## 📅 타임라인 (총 18-24시간)

```
Day 1 (8시간)
├─ Stage 1: 데이터 인프라 (3-4시간)
└─ Stage 2: 백엔드 API (4-5시간)

Day 2 (8시간)
├─ Stage 3: 프론트엔드 (3-4시간)
├─ Stage 4: 모바일 빌드 (2-3시간)
└─ Phase 1 MVP 완성 테스트 (1시간)

Day 3 (6-8시간)
└─ Stage 5: Phase 2 구현 (6-8시간)
```

---

## 🎯 마일스톤

### **Milestone 1: 데이터 준비 완료** (Day 1 오전)
```
✅ Supabase 테이블 생성
✅ 3,000+ 건 데이터 업로드
✅ 자동화 파이프라인 작동
```

### **Milestone 2: Phase 1 MVP 완성** (Day 2 저녁)
```
✅ 백엔드 API 작동
✅ 프론트엔드 UI 완성
✅ APK 빌드 성공
✅ Share → 앱 검사 작동
```

### **Milestone 3: Phase 2 완성** (Day 3 저녁)
```
✅ 백그라운드 자동 감지
✅ 실시간 알림
✅ 전체 기능 통합 테스트
```

---

## 💡 핵심 결정 사항

### **1. 서버 배포 방식**
```
선택지:
A. Docker Compose (Railway/Render)
B. Vercel (Frontend) + Render (Backend)

추천: A (초기에는 간단한 구조)
```

### **2. 데이터 정제 우선순위**
```
높음: 네이버, 구글 (한국어, 일일 업데이트)
중간: Reddit, 해외 뉴스 (번역 필요, 주간 업데이트)
낮음: 이미지 OCR (처리 시간 오래 걸림)

추천: 네이버/구글 먼저 → 나머지는 백그라운드
```

### **3. Phase 1 vs Phase 2 우선순위**
```
Phase 1 (Share Intent):
- 빠른 MVP
- 사용자 테스트 가능
- 피드백 수집

Phase 2 (Accessibility):
- 실제 사용 가치 높음
- 개발 시간 오래 걸림
- 권한 이슈 복잡

추천: Phase 1 완성 → 테스트 → Phase 2
```

---

## 🚀 추천 실행 순서

### **지금 바로 시작할 것**
```
1. Supabase 테이블 생성 (30분)
2. 1년치 데이터 업로드 테스트 (1시간)
3. 백엔드 룰 엔진 개발 (2시간)
```

### **오늘 안에 완료할 것**
```
Stage 1 + Stage 2 (데이터 + 백엔드)
→ 내일부터 프론트엔드 통합 가능
```

---

## ❓ 최종 확인

**Q1. Phase 2까지 전부 구현?**
→ Yes: 전체 3일 소요
→ No (Phase 1만): 2일 소요

**Q2. 데이터 정제 어디까지?**
→ 전체 (OCR + 번역 포함): 느림
→ 텍스트만 먼저: 빠름

**Q3. 배포는 언제?**
→ Phase 1 완성 후: 빠른 피드백
→ Phase 2 완성 후: 완전한 기능

---

## 🎯 제 추천

**"Bottom-Up 방식"**

```
1️⃣ Supabase 테이블 생성 (지금)
2️⃣ 백엔드 룰 엔진 개발 (오늘)
3️⃣ 프론트엔드 통합 (내일)
4️⃣ Phase 1 MVP 완성 (내일)
5️⃣ Phase 2 구현 (다음)
```

이유:
- ✅ 데이터부터 쌓으면서 백엔드 개발
- ✅ 백엔드가 준비되면 프론트엔드 빠르게 연결
- ✅ Phase 1 완성 후 실제 테스트 가능
- ✅ Phase 2는 Phase 1 피드백 반영 가능

---

**어떤 방식으로 진행할까요?** 🤔

1. **제 추천대로** (Bottom-Up)
2. **다른 순서 제안**
3. **특정 Stage만 먼저**
