# 피싱체커 백엔드 API

FastAPI 기반의 피싱 메시지 분석 백엔드 서버입니다.

## 🚀 기술 스택

- **Framework**: FastAPI 0.109.0
- **Server**: Uvicorn 0.27.0
- **Database**: Supabase
- **API**: Google Safe Browsing, Gemini

## 📁 프로젝트 구조

```
backend/
├── app/
│   ├── main.py                 # FastAPI 앱 엔트리포인트
│   ├── api/v1/
│   │   ├── analyze.py          # 메시지 분석 API
│   │   └── stats.py            # 통계 조회 API
│   ├── core/
│   │   ├── rule_engine.py      # 룰 기반 피싱 검사 엔진
│   │   ├── url_checker.py      # URL 안전성 검사 (Google Safe Browsing)
│   │   └── scorer.py           # 점수 계산 및 권장사항 생성
│   ├── schemas/
│   │   └── request.py          # Pydantic 모델 (요청/응답)
│   └── storage/
│       └── supabase.py         # Supabase 연결 관리
├── requirements.txt
├── test_api.sh                 # API 테스트 스크립트
└── README.md
```

## 🎨 주요 기능

### 1. 메시지 분석 API
- **엔드포인트**: `POST /api/v1/analyze`
- **기능**:
  - 키워드 기반 룰 검사 (46개 룰)
  - URL 패턴 검사 (6개 단축 URL)
  - Google Safe Browsing API를 통한 URL 안전성 검사
  - 위험도 점수 계산 (0-100)
  - 피싱 유형 자동 감지
  - 맞춤형 권장사항 생성

### 2. 통계 API
- **엔드포인트**: `GET /api/v1/stats`
- **기능**:
  - 전체 뉴스/이미지 수 조회
  - 최근 피싱 유형 분포
  - 일별 통계 (최근 7일)

### 3. 헬스체크
- **엔드포인트**: `GET /health`
- **기능**: 서버 상태 확인

## 🛠️ 설치 및 실행

### 1. 환경 설정

```bash
# .env 파일 생성 (루트 디렉토리)
GOOGLE_SAFE_BROWSING_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_key
```

### 2. 의존성 설치

```bash
cd backend
pip install -r requirements.txt
```

### 3. 서버 실행

```bash
# 개발 모드 (자동 리로드)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8888

# 프로덕션 모드
uvicorn app.main:app --host 0.0.0.0 --port 8888 --workers 4
```

### 4. API 문서 확인

- **Swagger UI**: http://localhost:8888/docs
- **ReDoc**: http://localhost:8888/redoc

## 🧪 테스트

### 자동 테스트 스크립트

```bash
chmod +x test_api.sh
./test_api.sh
```

### 수동 테스트

```bash
# 위험한 메시지 분석
curl -X POST http://localhost:8888/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"message": "긴급! 국세청입니다. 계좌가 정지되었습니다. 비밀번호를 입력하세요."}'

# 안전한 메시지 분석
curl -X POST http://localhost:8888/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"message": "안녕하세요. 내일 점심 약속 잡으실래요?"}'
```

## 📊 룰 엔진

### 키워드 카테고리 (총 46개 룰)

1. **기관사칭** (10개)
   - 국세청, 경찰청, 검찰청, 금융감독원
   - 은행, 카카오, 네이버, 택배, 쿠팡 등

2. **긴급성** (4개)
   - 즉시, 긴급, 24시간, 오늘 안

3. **금전요구** (6개)
   - 송금, 계좌이체, 입금, 상품권, 기프티콘, 환불

4. **개인정보** (8개)
   - 계좌번호, 비밀번호, 주민번호, 본인확인
   - 인증번호, 카드번호, CVC, CVV

5. **협박** (6개)
   - 정지, 체포, 고소, 고발, 압수수색, 소환장

6. **유인** (4개)
   - 당첨, 무료, 지원금, 환급

7. **링크유도** (6개)
   - 클릭, 링크, 접속, 다운로드, apk, 설치

8. **URL 패턴** (6개)
   - bit.ly, tinyurl.com, goo.gl, ow.ly, han.gl, me2.do

### 점수 계산

- **매우 위험** (35-40점): 기관사칭(주요), 체포, 비밀번호, 주민번호
- **위험** (25-30점): 금융사칭, 송금, 본인확인, 정지
- **주의** (15-20점): 긴급, 당첨, 단축URL, 링크

### 위험도 수준

- **safe** (0-20점): 안전
- **medium** (21-50점): 주의 필요
- **high** (51-80점): 위험
- **critical** (81-100점): 매우 위험

## 📝 API 명세

### POST /api/v1/analyze

**요청**:
```json
{
  "message": "검사할 메시지 내용",
  "urls": ["https://example.com"]  // 선택사항
}
```

**응답**:
```json
{
  "risk_score": 87,
  "risk_level": "critical",
  "is_phishing": true,
  "phishing_type": "정부기관사칭",
  "matched_rules": [
    {
      "category": "기관사칭",
      "matched_keyword": "국세청",
      "score": 40,
      "description": "정부 기관 사칭"
    }
  ],
  "url_check_results": [],
  "recommendations": [
    "⛔ 매우 위험한 피싱 메시지입니다!",
    "❌ 어떠한 요구에도 응하지 마세요."
  ],
  "analyzed_at": "2026-02-04T14:30:00Z"
}
```

### GET /api/v1/stats

**응답**:
```json
{
  "total_news": 3142,
  "total_images": 400,
  "recent_phishing_types": [
    {"type": "금융사칭", "count": 450},
    {"type": "택배사칭", "count": 320}
  ],
  "daily_stats": [...]
}
```

## 🔒 보안

- CORS 설정 (프론트엔드 연동)
- API 키 환경 변수 관리
- Google Safe Browsing API를 통한 실시간 URL 검증

## 🐛 알려진 이슈

- 의존성 충돌 경고 (pydantic 버전) - 기능에는 영향 없음
- URL 추출은 간단한 정규식 사용 (복잡한 URL은 놓칠 수 있음)

## 📄 라이선스

MIT License
