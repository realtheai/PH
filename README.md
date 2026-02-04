# app

메시지 탐지 앱

## 🎯 프로젝트 개요

탐지하는 모바일 앱입니다.

### Phase 1 (MVP)
- Share → App 검사 흐름
- 룰 기반 + URL 체크
- 위험도 점수 (0-100)

### Phase 2
- 백그라운드 자동 감지 (Accessibility Service)
- 온디바이스 우선 판정

## 📁 프로젝트 구조

```
phishingapp/
├── backend/          # FastAPI 서버
├── frontend/         # Next.js 14 (App Router)
├── mobile/           # Capacitor + Android
├── data/             # 데이터 수집/정제
├── database/         # DB 스키마
├── scripts/          # 크롤링/자동화 스크립트
└── docs/             # 문서
```

## 🚀 시작하기

### 백엔드 실행
```bash
cd backend
pip install -r requirements.txt
python -m app.main
```

### 프론트엔드 실행
```bash
cd frontend
npm install
npm run dev
```

## 📊 기술 스택

- **Backend**: FastAPI, Python, Supabase
- **Frontend**: Next.js 14, Tailwind CSS, Zustand
- **Mobile**: Capacitor, Kotlin
- **AI**: Gemini API, Google Safe Browsing API

## 📝 문서

- [PRD](./data/prd_architecture.md)
- [개발 계획](./DEVELOPMENT_PLAN.md)
- [데이터 자동화](./DATA_DB_AUTOMATION.md)

## 🔑 환경 변수

`.env` 파일에 다음 키들을 설정하세요:

```bash
# Supabase
SUPABASE_URL=
SUPABASE_ANON_KEY=

# Google APIs
GOOGLE_SAFE_BROWSING_API_KEY=
GEMINI_API_KEY=

# Naver API
NAVER_CLIENT_ID=
NAVER_CLIENT_SECRET=
```

## 📄 라이선스

MIT License
