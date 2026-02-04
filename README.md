# 🛡️ 피싱체커 (PhishingApp)

**AI 기반 실시간 피싱 메시지 탐지 앱**

의심스러운 메시지를 즉시 분석하여 피싱 위험도를 판정하고, 사용자를 보호합니다.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🎉 Phase 1 MVP 완성!

- ✅ **웹 앱**: Next.js 16 기반 9개 화면
- ✅ **백엔드 API**: FastAPI 기반 46개 룰 엔진
- ✅ **Android 앱**: Capacitor + Share Intent (APK 4.4MB)
- ✅ **전체 통합**: 공유 → 분석 → 결과 → 신고

---

## 🚀 핵심 기능

### 1. 실시간 피싱 분석
- 46개 키워드 룰 기반 검사
- Google Safe Browsing API 연동
- 0-100점 위험도 점수
- 4단계 위험 수준 (safe/medium/high/critical)

### 2. Share Intent
- 다른 앱(메시지, 카카오톡 등)에서 "공유" 클릭
- 피싱체커로 자동 전달
- 즉시 분석 시작

### 3. 검사 내역
- 과거 검사 기록 자동 저장
- 위험도별 필터링
- 재검사 기능

### 4. 신고 안내
- 경찰청 (112)
- 한국인터넷진흥원 KISA (118)
- 금융감독원 (1332)

---

## 📁 프로젝트 구조

```
phishingapp/
├── frontend/           # Next.js 웹앱 + Android 앱
│   ├── app/           # 9개 화면
│   └── android/       # Capacitor Android 프로젝트
├── backend/           # FastAPI 백엔드 API
│   └── app/           # 룰 엔진, URL 체커
├── data/              # 피싱 데이터 (3,142건)
├── scripts/           # 데이터 수집 스크립트 (25개)
└── docs/              # 문서
```

---

## 🛠️ 기술 스택

### 프론트엔드
- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4
- **Mobile**: Capacitor

### 백엔드
- **Framework**: FastAPI
- **Language**: Python 3.11
- **Database**: Supabase
- **APIs**: Google Safe Browsing, Gemini

### 모바일
- **Platform**: Android
- **Build**: Gradle
- **Share**: Intent Filter

---

## 🚀 빠른 시작

### 1. 백엔드 실행

```bash
# 환경 변수 설정
cp .env.example .env
# .env 파일에 API 키 입력

# 의존성 설치 및 실행
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8888
```

**API 문서**: http://localhost:8888/docs

### 2. 프론트엔드 실행

```bash
cd frontend
npm install
npm run dev
```

**웹 앱**: http://localhost:3000

### 3. Android APK 빌드

```bash
cd frontend
npm run build
npx cap sync android
cd android
./gradlew assembleDebug
```

**APK 위치**: `android/app/build/outputs/apk/debug/app-debug.apk`

---

## 📱 앱 사용법

### Share Intent 방식 (추천)

1. **메시지 앱**에서 의심 메시지 선택
2. **"공유"** 버튼 클릭
3. **"피싱체커"** 선택
4. 자동으로 분석 시작
5. 위험도 결과 확인
6. 필요시 신고

### 직접 입력 방식

1. 피싱체커 앱 실행
2. 메시지 내용 입력
3. "검사하기" 버튼 클릭
4. 결과 확인

---

## 📊 룰 엔진

### 46개 키워드 룰

- **기관사칭** (10개): 국세청, 경찰청, 은행 등
- **긴급성** (4개): 즉시, 긴급, 24시간 등
- **금전요구** (6개): 송금, 상품권, 환불 등
- **개인정보** (8개): 비밀번호, 주민번호 등
- **협박** (6개): 정지, 체포, 고소 등
- **유인** (4개): 당첨, 무료, 지원금 등
- **링크유도** (6개): 클릭, 다운로드, apk 등
- **URL 패턴** (6개): bit.ly, tinyurl 등

### 위험도 판정

| 점수 | 수준 | 설명 |
|------|------|------|
| 0-20 | safe | 안전 |
| 21-50 | medium | 주의 필요 |
| 51-80 | high | 위험 |
| 81-100 | critical | 매우 위험 |

---

## 🧪 API 테스트

### 테스트 스크립트 실행

```bash
cd backend
chmod +x test_api.sh
./test_api.sh
```

### 수동 테스트

```bash
# 위험한 메시지
curl -X POST http://localhost:8888/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"message": "긴급! 국세청입니다. 계좌가 정지되었습니다."}'

# 안전한 메시지
curl -X POST http://localhost:8888/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"message": "안녕하세요. 내일 점심 약속 잡으실래요?"}'
```

---

## 📖 문서

- [개발 계획서](DEVELOPMENT_PLAN.md) - 전체 개발 로드맵
- [Stage 2 완료](STAGE2_COMPLETE.md) - 백엔드 API 개발
- [Stage 3 완료](STAGE3_COMPLETE.md) - 프론트엔드 통합
- [Stage 4 완료](STAGE4_COMPLETE.md) - 모바일 빌드
- [프로젝트 완료](PROJECT_COMPLETE.md) - 최종 완성 보고서
- [백엔드 가이드](backend/README.md)
- [프론트엔드 가이드](frontend/README.md)
- [Android 가이드](frontend/android/README.md)

---

## 🎯 개발 현황

### ✅ 완료
- [x] Stage 2: 백엔드 API (46개 룰, URL 체커)
- [x] Stage 3: 프론트엔드 (9개 화면, 다크 모드)
- [x] Stage 4: 모바일 빌드 (Share Intent, APK)
- [x] **Phase 1 MVP 완성!**

### ⏳ 예정
- [ ] Stage 1: 데이터 인프라 (Supabase 테이블, 3,142건 업로드)
- [ ] Phase 2: 백그라운드 자동 감지 (Accessibility Service)
- [ ] 프로덕션 배포 (Google Play Store)

---

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

## 📞 문의

- **이메일**: phishingapp@example.com
- **이슈**: [GitHub Issues](https://github.com/yourusername/phishingapp/issues)

---

## 🙏 감사의 말

- Google Safe Browsing API
- Supabase
- Gemini API
- Capacitor
- Next.js & FastAPI 커뮤니티

---

**🎊 피싱으로부터 안전한 세상을 만듭니다 🎊**
