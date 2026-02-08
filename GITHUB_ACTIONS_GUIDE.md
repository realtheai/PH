# GitHub Actions 배포 가이드

## 📋 배포 단계 요약

### 1단계: GitHub Repository 설정
```bash
# 1. GitHub에 새 저장소 생성 (예: phishing-detection-api)

# 2. 로컬 저장소 초기화 (아직 안했다면)
cd /home/realtheai/phishingapp
git init
git add .
git commit -m "Initial commit: OpenAI 임베딩 전환 완료"

# 3. GitHub 저장소와 연결
git remote add origin https://github.com/YOUR_USERNAME/phishing-detection-api.git
git branch -M main
git push -u origin main
```

---

### 2단계: GitHub Secrets 설정

Repository → Settings → Secrets and variables → Actions → New repository secret

**필수 Secrets:**
```
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...
GOOGLE_API_KEY=AIza...
GOOGLE_SAFE_BROWSING_API_KEY=AIza...
```

**선택적 (프론트엔드 있는 경우):**
```
VERCEL_TOKEN=...
VERCEL_ORG_ID=...
VERCEL_PROJECT_ID=...
```

---

### 3단계: GitHub Actions 워크플로우 파일 생성

`.github/workflows/deploy-backend.yml` 파일을 생성합니다.

---

### 4단계: Docker Hub 설정 (옵션 1 - Docker 사용 시)

**Docker Hub Secrets 추가:**
```
DOCKER_USERNAME=your_username
DOCKER_PASSWORD=your_password
```

**또는 GitHub Container Registry 사용 (권장):**
```
GHCR_TOKEN=ghp_... (GitHub Personal Access Token)
```

---

### 5단계: 배포 환경 선택

#### 옵션 A: **Render.com** (권장 - 무료)
- 자동 Docker 빌드
- 무료 플랜 제공
- 환경 변수 관리 편리

#### 옵션 B: **Railway.app** (권장)
- GitHub 연동 자동 배포
- 무료 크레딧 제공
- PostgreSQL 호스팅 가능

#### 옵션 C: **Fly.io**
- 무료 티어 제공
- 글로벌 엣지 배포
- CLI 기반 배포

#### 옵션 D: **AWS EC2 / Azure / GCP**
- 완전한 제어
- GitHub Actions에서 SSH 배포
- 비용 발생

---

### 6단계: 배포 트리거

```bash
# main 브랜치에 push하면 자동 배포
git add .
git commit -m "feat: 배포 준비 완료"
git push origin main
```

---

## 🎯 추천 배포 방법

### 방법 1: Render.com (가장 쉬움)

1. Render.com 가입
2. "New Web Service" 클릭
3. GitHub 저장소 연결
4. 설정:
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3.11
5. 환경 변수 추가 (위의 Secrets)
6. Deploy 클릭

**배포 완료!** ✅

---

### 방법 2: Railway.app (추천)

1. Railway.app 가입
2. "New Project" → "Deploy from GitHub repo"
3. 저장소 선택
4. 환경 변수 추가
5. 자동 배포 시작

**Railway CLI로도 가능:**
```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

---

### 방법 3: GitHub Actions + Docker Hub + VPS

1. VPS 준비 (예: DigitalOcean, AWS EC2)
2. Docker Hub에 이미지 푸시 (GitHub Actions)
3. VPS에서 이미지 pull 및 실행

**필요한 파일:** `.github/workflows/deploy-backend.yml`

---

## 📁 필수 파일 체크리스트

### 백엔드 배포에 필요한 파일들

✅ `backend/requirements.txt` - OpenAI 포함됨
✅ `backend/app/` - 애플리케이션 코드
✅ `backend/Dockerfile` - Docker 이미지 빌드용
✅ `.env.example` - 환경 변수 템플릿
✅ `docker-compose.yml` - 로컬 테스트용

### 프론트엔드 배포 (있는 경우)

✅ `frontend/package.json`
✅ `frontend/.env.example`
✅ Vercel/Netlify 설정

---

## 🔒 보안 체크리스트

### 배포 전 확인사항

- [ ] `.env` 파일이 `.gitignore`에 포함되어 있음
- [ ] GitHub Secrets에 모든 API 키 등록 완료
- [ ] `SUPABASE_SERVICE_ROLE_KEY`는 절대 노출 금지
- [ ] CORS 설정 확인 (프론트엔드 도메인만 허용)
- [ ] Rate Limiting 설정 (DDoS 방지)
- [ ] 환경 변수로 민감 정보 관리

---

## 🚀 배포 후 테스트

### API 엔드포인트 테스트

```bash
# 1. Health Check
curl https://your-api.render.com/

# 2. 피싱 분석 테스트
curl -X POST https://your-api.render.com/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "message": "엄마, 나 주식으로 돈 좀 벌어볼까 하는데 어때?"
  }'

# 3. 벡터 검색 확인
# similar_cases_count > 0 인지 확인
```

---

## 📊 모니터링 설정

### 필수 모니터링 항목

1. **API 응답 시간**
   - 목표: < 3초

2. **OpenAI API 사용량**
   - 일일 비용 모니터링
   - 한도 설정

3. **Supabase 연결**
   - 벡터 검색 성공률
   - DB 쿼리 속도

4. **에러 로그**
   - 500 에러 발생 시 알림
   - 로그 수집 (Sentry, LogRocket)

---

## 💰 예상 비용

### 무료 티어로 시작 가능

**Render.com 무료 플랜:**
- 0 GB RAM, 0.1 vCPU
- 750시간/월 (한 달 내내 가능)
- 15분 비활성 시 슬립 모드

**Railway.app:**
- $5 무료 크레딧/월
- 초과 시 사용량 기반 과금

**OpenAI API:**
- 임베딩: $0.0001/1K 토큰
- GPT-4o-mini: $0.15/1M 토큰
- **예상 비용: ~$1-5/월** (트래픽에 따라)

**Supabase:**
- 무료 플랜: 500MB DB, 2GB 전송
- 벡터 검색 무제한

---

## 🔄 CI/CD 파이프라인

### 자동화된 배포 흐름

```
코드 Push → GitHub Actions 트리거
    ↓
테스트 실행 (pytest, linting)
    ↓
Docker 이미지 빌드
    ↓
이미지 Registry 푸시
    ↓
배포 환경에 배포
    ↓
Health Check
    ↓
알림 (Slack, Discord)
```

---

## 📝 다음 단계

### 배포 완료 후 개선사항

1. **캐싱 추가**
   - Redis/Memcached로 유사 쿼리 캐싱
   - 응답 속도 10배 향상

2. **Rate Limiting**
   - IP 기반 요청 제한
   - API 키 기반 인증

3. **로그 분석**
   - 피싱 탐지 정확도 추적
   - False Positive 분석

4. **A/B 테스트**
   - 다른 LLM 모델 비교
   - 임베딩 모델 성능 비교

5. **알림 시스템**
   - 고위험 피싱 탐지 시 관리자 알림
   - 일일 리포트 자동 생성

---

## ❓ 문제 해결

### 배포 중 자주 발생하는 이슈

**1. "Module not found" 오류**
```bash
# 해결: requirements.txt 확인
pip freeze > requirements.txt
```

**2. "Connection timeout" (OpenAI)**
```python
# 해결: timeout 설정
client = OpenAI(timeout=30.0)
```

**3. "Out of memory"**
```yaml
# 해결: 메모리 증가 (Render.com)
# 유료 플랜으로 업그레이드 (512MB → 1GB)
```

**4. "CORS error"**
```python
# 해결: CORS 미들웨어 추가
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.com"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📞 지원

배포 중 문제가 발생하면:
1. GitHub Issues에 문제 등록
2. 로그 확인: `railway logs` 또는 Render 대시보드
3. 환경 변수 재확인
4. Docker 로컬 테스트: `docker-compose up`

---

## ✅ 최종 체크리스트

배포 전 마지막 확인:

- [ ] 모든 테스트 통과
- [ ] `.gitignore`에 `.env` 포함
- [ ] GitHub Secrets 등록 완료
- [ ] `requirements.txt`에 openai 포함
- [ ] Docker 이미지 로컬 테스트 완료
- [ ] CORS 설정 확인
- [ ] Health check 엔드포인트 동작 확인
- [ ] 실제 피싱 메시지로 API 테스트 완료
- [ ] 모니터링 설정 완료

**모든 항목 체크 완료 시 배포 준비 완료!** 🎉
