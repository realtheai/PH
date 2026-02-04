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
- [x] Next.js 프로젝트 설정
- [x] Tailwind CSS 커스텀 테마 (Stitch 스타일 반영)
- [x] 공통 컴포넌트 (Header, BottomNav)
- [x] 9개 주요 화면 완성
- [x] 다크 모드 지원
- [x] LocalStorage 기반 데이터 저장
- [x] Mock 분석 로직 (간단한 키워드 기반 판정)
- [x] 반응형 UI (모바일 최적화)

### ⏳ 대기 중 (백엔드 연동 필요)
- [ ] 실제 API 연동 (`POST /api/v1/analyze`)
- [ ] 실시간 피싱 뉴스 데이터 표시
- [ ] 통계 데이터 조회
- [ ] 사용자 인증 (Phase 2)

## 📱 모바일 빌드 (Phase 1 완성 목표)

프론트엔드 완성 후 다음 단계:

1. **Capacitor 설정**
   ```bash
   npm install @capacitor/core @capacitor/cli
   npx cap init
   npx cap add android
   ```

2. **Android Share Intent 구현**
   - 다른 앱에서 "공유" → 피싱체커로 메시지 전달
   - ShareReceiverActivity.kt 작성

3. **APK 빌드**
   ```bash
   npx cap sync
   cd android
   ./gradlew assembleDebug
   ```

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

## 🔌 API 연동 가이드 (백엔드 준비 후)

### 1. 환경 변수 설정
```bash
# .env.local 파일 생성
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 2. API 클라이언트 작성
```typescript
// app/lib/api.ts
export async function analyzeMessage(message: string) {
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  });
  return response.json();
}
```

### 3. 분석 페이지 수정
```typescript
// app/analyze/page.tsx
const result = await analyzeMessage(message);
```

## 📝 TODO

- [ ] API 연동 (백엔드 완성 후)
- [ ] 에러 핸들링 개선
- [ ] 로딩 상태 관리 개선 (Suspense)
- [ ] SEO 최적화
- [ ] PWA 설정 (오프라인 지원)
- [ ] E2E 테스트 (Playwright)
- [ ] 성능 최적화 (이미지 lazy loading 등)

## 🐛 알려진 이슈

- LocalStorage는 브라우저 종료 시 데이터가 유지되지 않을 수 있음 → Phase 2에서 서버 저장으로 전환
- Mock 분석 로직은 간단한 키워드 기반이므로 정확도가 낮음 → 백엔드 룰 엔진 연동 필요

## 📄 라이선스

MIT License
