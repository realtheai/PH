# 피싱체커 프론트엔드

Next.js 15 기반의 피싱 탐지 웹 애플리케이션 프론트엔드입니다.

## 🚀 기술 스택

- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4
- **Icons**: Material Symbols Outlined
- **Font**: Public Sans

## 📁 프로젝트 구조

```
frontend/
├── app/
│   ├── components/          # 공통 컴포넌트
│   │   ├── Header.tsx       # 헤더 컴포넌트
│   │   └── BottomNav.tsx    # 하단 네비게이션
│   ├── page.tsx             # 메인 페이지 (메시지 입력)
│   ├── analyze/             # 분석 진행 화면
│   ├── result/
│   │   ├── high-risk/       # 고위험 결과 화면
│   │   └── safe/            # 안전 결과 화면
│   ├── history/             # 검사 내역 페이지
│   ├── report/              # 신고 페이지
│   ├── settings/            # 설정 페이지
│   ├── layout.tsx           # 루트 레이아웃
│   └── globals.css          # 글로벌 스타일
└── package.json
```

## 🎨 주요 화면

### 1. 메인 화면 (`/`)
- 메시지 입력 텍스트 영역
- 검사하기 버튼
- 붙여넣기 버튼
- 피싱 예시 팁 카드

### 2. 분석 진행 화면 (`/analyze`)
- 로딩 애니메이션
- 분석 단계별 진행 상태
- 자동으로 결과 페이지로 이동 (3초)

### 3. 결과 화면
- **고위험** (`/result/high-risk`): 위험도 높음, 신고 버튼
- **안전** (`/result/safe`): 안전함, 주의사항 안내

### 4. 검사 내역 (`/history`)
- 과거 검사 기록 목록
- 위험도 배지 표시
- 클릭 시 상세 결과 보기

### 5. 신고 페이지 (`/report`)
- 경찰청, KISA, 금융감독원 연락처
- 전화 걸기 / 웹사이트 열기
- 신고 준비사항 안내

### 6. 설정 페이지 (`/settings`)
- 다크 모드 토글
- 알림 설정
- 검사 내역 삭제
- 앱 정보

## 🛠️ 개발 서버 실행

```bash
# 의존성 설치
npm install

# 개발 서버 시작
npm run dev

# 프로덕션 빌드
npm run build

# 프로덕션 서버 시작
npm start
```

개발 서버: http://localhost:3000

## 🎯 현재 구현 상태

### ✅ 완료
- [x] Next.js 프로젝트 설정 (App Router)
- [x] Tailwind CSS 커스텀 테마
- [x] 공통 컴포넌트 (Header, BottomNav)
- [x] 9개 주요 화면 완성
- [x] 다크 모드 지원
- [x] LocalStorage 기반 데이터 저장
- [x] 반응형 UI (모바일 최적화)
- [x] **백엔드 API 연동** (`POST /api/v1/analyze`)
- [x] **Capacitor 모바일 빌드** (Android APK)
- [x] **Static HTML Export** (조건부 빌드)
- [x] **Vercel 웹 배포** + **Railway 백엔드 배포**

### 🚀 배포 완료
- **웹**: https://phishingchecker.vercel.app
- **백엔드**: https://ph-production-4b6a.up.railway.app
- **모바일**: APK 빌드 완료 (`app-debug.apk`)

## 📱 모바일 빌드 (Capacitor + Android)

### ✅ 현재 설정 완료
- Capacitor 3.x 설치 및 설정
- Android 프로젝트 생성 (`frontend/android/`)
- Static HTML Export 설정 (모바일 빌드 전용)

### 🚀 APK 빌드 방법

```bash
# 1. 프론트엔드 → 모바일 빌드 (Static Export)
npm run build:mobile

# 2. Capacitor 동기화 (out/ → android/app/src/main/assets/public/)
npx cap sync android

# 3. Android Studio 열기 (선택)
npx cap open android

# 4. APK 빌드
cd android
./gradlew clean assembleDebug

# 빌드된 APK 위치
# android/app/build/outputs/apk/debug/app-debug.apk
```

### 📌 주요 설정 파일

**`package.json`** - 모바일 전용 빌드 스크립트
```json
{
  "scripts": {
    "build:mobile": "BUILD_TARGET=mobile next build",
    "cap:sync": "npm run build:mobile && npx cap sync",
    "cap:android": "npm run cap:sync && npx cap open android"
  }
}
```

**`next.config.ts`** - 조건부 Static Export
```typescript
const nextConfig: NextConfig = {
  output: process.env.BUILD_TARGET === 'mobile' ? 'export' : undefined,
  images: { unoptimized: true },
  trailingSlash: true,
};
```

**`capacitor.config.ts`** - Capacitor 설정
```typescript
{
  appId: 'com.phishingchecker.app',
  appName: 'PhishingChecker',
  webDir: 'out',
  server: {
    androidScheme: 'https'
  }
}
```

### 🔄 Static Export vs 일반 빌드
| 빌드 타입 | 용도 | 명령어 | 출력 |
|----------|-----|--------|------|
| **일반 빌드** | Vercel 웹 배포 | `npm run build` | `.next/` |
| **모바일 빌드** | Capacitor APK | `npm run build:mobile` | `out/` (HTML) |



## 🔧 Mock 데이터 구조

현재 LocalStorage에 저장되는 데이터:

```typescript
// 분석 결과
interface AnalysisResult {
  message: string;
  timestamp: string;
  riskLevel: "high" | "safe";
  score: number; // 0-100
}

// 검사 내역
scanHistory: AnalysisResult[]

// 설정
darkMode: boolean
notifications: boolean
autoScan: boolean
```

## 🎨 디자인 시스템

### 컬러 팔레트
- **Primary**: `#1f3a60` (네이비 블루)
- **Danger**: `#d32f2f` (빨강)
- **Success**: `#4caf50` (초록)
- **Warning**: `#ff9800` (오렌지)
- **Background Light**: `#f6f7f8`
- **Background Dark**: `#14181e`

### 반경 (Border Radius)
- `DEFAULT`: 0.25rem
- `lg`: 0.5rem
- `xl`: 0.75rem
- `full`: 9999px

### 폰트
- **Display**: Public Sans (400, 500, 600, 700)

## 🔌 백엔드 API 연동 (완료)

### 환경 변수 설정
```bash
# .env.local 파일 (로컬 개발)
NEXT_PUBLIC_API_URL=http://localhost:8000

# Vercel 배포 (프로덕션)
NEXT_PUBLIC_API_URL=https://ph-production-4b6a.up.railway.app
```

### API 엔드포인트
| 엔드포인트 | 메서드 | 용도 |
|-----------|--------|------|
| `/api/v1/analyze` | POST | 메시지 분석 |
| `/api/v1/stats` | GET | 통계 조회 |
| `/health` | GET | 헬스체크 |

### 사용 예시
```typescript
// 메시지 분석 (app/analyze/page.tsx에서 사용)
const response = await fetch(`${API_URL}/api/v1/analyze`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: userInput }),
});
const result = await response.json();
```



## 📄 라이선스

MIT License
