# 🛡️ Phishing Detection API

AI 기반 피싱/스미싱 탐지 시스템

## 🚀 주요 기능

- **실시간 피싱 탐지**: 메시지를 분석하여 피싱 여부 판단
- **벡터 검색 (RAG)**: 1,360개 실제 피싱 사례 기반 유사도 분석
- **LLM 분석**: OpenAI GPT-4o-mini 기반 정교한 판단
- **URL 검사**: Google Safe Browsing API 통합
- **규칙 기반 탐지**: 키워드, 패턴 매칭

## 📊 시스템 아키텍처

```
사용자 메시지
    ↓
FastAPI Backend
    ↓
1. 규칙 기반 검사 (키워드, URL)
2. LLM 분석 (GPT-4o-mini)
3. 벡터 검색 (OpenAI Embeddings + Supabase)
4. 종합 위험도 계산
    ↓
피싱 여부 + 위험도 + 권장사항
```

## 🛠️ 기술 스택

### Backend
- **Framework**: FastAPI
- **LLM**: OpenAI GPT-4o-mini
- **Embedding**: OpenAI text-embedding-3-small
- **Database**: Supabase (PostgreSQL + pgvector)
- **URL Check**: Google Safe Browsing API
- **Deployment**: Docker

### 데이터
- **실제 피싱 사례**: 1,360개
  - 이미지 OCR: 373개
  - 뉴스 기사: 987개
- **출처**: Google Images, Naver News, Google News

## 🏃 빠른 시작

### 1. 환경 설정

```bash
# 저장소 클론
git clone https://github.com/YOUR_USERNAME/phishing-detection-api.git
cd phishing-detection-api

# 환경 변수 설정
cp .env.example .env
# .env 파일을 열어 API 키 입력
```

### 2. 로컬 실행

#### Docker 사용 (권장)
```bash
docker-compose up --build
```

#### Python 직접 실행
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 3. API 테스트

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "message": "엄마, 나 주식으로 돈 좀 벌어볼까 하는데 어때?"
  }'
```

**응답 예시:**
```json
{
  "risk_score": 66,
  "risk_level": "high",
  "is_phishing": true,
  "phishing_type": "가족사칭",
  "similar_cases_count": 1,
  "llm_analysis": {
    "is_phishing": true,
    "confidence": 0.85,
    "risk_score": 75
  },
  "recommendations": [
    "🚨 위험한 메시지입니다. 즉시 대응을 중단하세요."
  ]
}
```

## 📡 API 엔드포인트

### POST `/api/v1/analyze`
메시지 분석

**Request:**
```json
{
  "message": "분석할 메시지",
  "image_url": "https://example.com/image.jpg"  // 선택
}
```

**Response:**
```json
{
  "risk_score": 0-100,
  "risk_level": "safe|low|medium|high|critical",
  "is_phishing": true|false,
  "phishing_type": "유형",
  "matched_rules": [],
  "url_check_results": [],
  "similar_cases_count": 0,
  "recommendations": []
}
```

### GET `/health`
서버 상태 확인

## 🔐 환경 변수

필수 환경 변수를 `.env` 파일에 설정:

```env
# OpenAI
OPENAI_API_KEY=sk-...

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...

# Google
GOOGLE_API_KEY=AIza...
GOOGLE_SAFE_BROWSING_API_KEY=AIza...
```

## 🚢 배포

### Render.com (권장)
1. Render.com 가입
2. GitHub 저장소 연결
3. 환경 변수 설정
4. 자동 배포 시작

자세한 내용: [GITHUB_ACTIONS_GUIDE.md](./GITHUB_ACTIONS_GUIDE.md)

### Railway.app
```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

## 📊 성능

- **응답 시간**: ~3초 (LLM + 벡터 검색)
- **정확도**: ~85% (실제 피싱 사례 기준)
- **처리량**: 100+ req/min
- **비용**: ~$1-5/월 (OpenAI API)

## 🧪 테스트

```bash
# 단위 테스트
pytest tests/ -v

# 커버리지
pytest tests/ --cov=app --cov-report=html

# 통합 테스트
python test_openai_embedding.py
```

## 📈 모니터링

- **Health Check**: `/health`
- **로그**: Render/Railway 대시보드
- **비용**: OpenAI Usage 대시보드

## 🤝 기여

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 라이선스

MIT License

## 👤 작성자

- GitHub: [@YOUR_USERNAME](https://github.com/YOUR_USERNAME)

## 🙏 감사의 말

- OpenAI GPT-4o-mini
- Supabase pgvector
- Google Safe Browsing API
- 실제 피싱 사례 데이터 제공자들

## 📞 지원

- Issues: [GitHub Issues](https://github.com/YOUR_USERNAME/phishing-detection-api/issues)
- Email: your-email@example.com

---

**⚠️ 주의사항:**
이 시스템은 보조 도구로 사용되어야 하며, 100% 정확도를 보장하지 않습니다. 의심스러운 메시지는 항상 공식 기관에 직접 확인하세요.
