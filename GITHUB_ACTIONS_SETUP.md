# 🚀 GitHub Actions 자동화 설정 가이드

## 📋 개요

매일 자동으로 피싱 데이터를 수집, 정제, 분류하는 파이프라인을 GitHub Actions로 구현했습니다.

## ⏰ 실행 스케줄

- **자동 실행**: 매일 UTC 00:00 (한국 시간 09:00)
- **수동 실행**: GitHub Actions 탭에서 `Run workflow` 버튼 클릭

## 🔧 GitHub Secrets 설정

GitHub 저장소 → Settings → Secrets and variables → Actions → New repository secret

### 필수 Secrets

#### 1. Naver API
```
NAVER_CLIENT_ID=<네이버 클라이언트 ID>
NAVER_CLIENT_SECRET=<네이버 클라이언트 시크릿>
```

#### 2. Gemini API (6개 키)
```
GEMINI_API_KEY_1=<Gemini API 키 1>
GEMINI_API_KEY_2=<Gemini API 키 2>
GEMINI_API_KEY_3=<Gemini API 키 3>
GEMINI_API_KEY_4=<Gemini API 키 4>
GEMINI_API_KEY_5=<Gemini API 키 5>
GEMINI_API_KEY_6=<Gemini API 키 6>
```

#### 3. OpenAI API
```
OPENAI_API_KEY=<OpenAI API 키>
```

#### 4. Supabase
```
SUPABASE_URL=<Supabase 프로젝트 URL>
SUPABASE_ANON_KEY=<Supabase Anon 키>
```

## 📊 파이프라인 단계

### 1️⃣ 크롤링 (데이터 수집)
- 네이버 API
- 구글 뉴스
- 구글 이미지
- Reddit
- 해외 뉴스

### 2️⃣ 이미지 OCR
- Gemini Vision API 사용
- 이미지에서 텍스트 추출

### 3️⃣ 텍스트 번역
- 영어 → 한국어
- Gemini + OpenAI Fallback

### 4️⃣ 콘텐츠 분류
- REAL_CASE / NEWS / NOISE 분류
- Few-shot Learning 사용

### 5️⃣ 피싱 유형 분류
- REAL_CASE만 세부 분류
- 가족사칭, 공공기관사칭 등

### 6️⃣ 중복 제거
- Sentence Embedding 기반
- 유사도 97% 이상 중복 제거

### 7️⃣ 완료 알림
- 파이프라인 완료 메시지

## 🔍 모니터링

### GitHub Actions 로그 확인
1. GitHub 저장소 → Actions 탭
2. 최신 워크플로우 실행 클릭
3. 각 단계별 로그 확인

### Supabase 대시보드 확인
1. Supabase 프로젝트 → Table Editor
2. `phishing_news` 테이블 확인
3. `phishing_images` 테이블 확인

## ⚠️ 주의사항

### API Rate Limit
- Gemini: 60 requests/min (Free tier)
- OpenAI: Fallback으로만 사용
- 각 단계에서 자동으로 Rate Limit 처리

### 에러 처리
- 각 단계는 `continue-on-error: true`로 설정
- 한 단계 실패해도 다음 단계 계속 진행
- 로그에서 실패 원인 확인 가능

### 비용 관리
- Gemini Free Tier: 일일 1500 requests
- OpenAI: Fallback으로만 사용하여 비용 최소화
- Supabase: Free Tier로 충분

## 🛠️ 수동 실행 방법

1. GitHub 저장소 → Actions 탭
2. "📊 Daily Phishing Data Pipeline" 선택
3. "Run workflow" 버튼 클릭
4. "Run workflow" 확인 버튼 클릭

## 📈 예상 실행 시간

- 크롤링: 5-10분
- OCR: 10-20분 (이미지 개수에 따라)
- 번역: 5-10분
- 분류: 10-20분
- 피싱 유형 분류: 10-20분
- 중복 제거: 5-10분

**총 예상 시간: 45-90분**

## 🐛 문제 해결

### Secrets 설정 오류
- GitHub Secrets가 올바르게 설정되었는지 확인
- Secrets 이름이 정확한지 확인 (대소문자 구분)

### API Rate Limit 초과
- Gemini API 키를 더 추가
- `.env` 파일에 `GEMINI_API_KEY_7`, `GEMINI_API_KEY_8` 등 추가

### Supabase 연결 오류
- Supabase URL과 Anon Key 확인
- Supabase 프로젝트가 활성 상태인지 확인

## 📝 로컬 테스트

GitHub Actions 실행 전 로컬에서 테스트:

```bash
# 1. 환경 변수 설정
cp .env.example .env
# .env 파일 수정

# 2. 개별 스크립트 테스트
python scripts/daily/crawl_naver_daily.py
python scripts/classify_data.py

# 3. 전체 파이프라인 테스트
bash scripts/test_pipeline.sh
```

## ✅ 체크리스트

- [ ] GitHub Secrets 설정 완료
- [ ] Supabase 테이블 생성 완료
- [ ] 로컬에서 스크립트 테스트 완료
- [ ] GitHub Actions 수동 실행 테스트
- [ ] 자동 스케줄 실행 확인

## 🎯 다음 단계

1. ✅ GitHub Actions 설정
2. ⏳ 백엔드 API 개발 (FastAPI)
3. ⏳ 프론트엔드 통합 (Next.js)
4. ⏳ 모바일 앱 빌드 (Capacitor)
5. ⏳ Phase 2 구현 (백그라운드 감지)
