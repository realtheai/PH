# 피싱·스캠 예방을 위한 서비스 개발 경진대회

## 📌 대회 기본 정보

- **대회명**: 피싱·스캠 예방을 위한 서비스 개발 경진대회
- **주최**: DataUniverse, 경찰청
- **카테고리**: 아이디어 | 사이버 보안 | 피싱·스캠 탐지 | MVP
- **상금**: 1,000만원
- **기간**: 2026.01.14 ~ 2026.02.11 10:00
- **참가인원**: 405명
- **종료까지**: D-12

---

## 🎯 대회 배경

스캠과 피싱 범죄는 해외 조직까지 연루되며 점점 더 정교해지고 있습니다.

누구나 피해자가 될 수 있는 만큼, 새로운 대응 아이디어가 필요합니다.

이번 대회는 **아이디어와 창의적 서비스 콘텐츠**를 찾기 위한 경진대회입니다.

---

## 📋 주제

### 메인 주제
**피싱·스캠 예방을 위한 서비스 개발**

### 예시 주제

#### ① AI 등을 활용한 피싱·스캠 위험을 실시간 분석하고 경고해주는 AI기반 탐지/경고 서비스
- AI를 활용하여 피싱/스캠 위험을 실시간으로 분석하고 경고

#### ② 개인의 피싱·스캠 위험도를 시각화하고 대응력을 인내하는 대시보드형 서비스  
- 개인의 피싱/스캠 위험도를 시각화하고 대응력을 높이는 대시보드

#### ③ 시시클릭이나 대화-퀴즈 등을 통해 경각심을 높이는 학습형 예방 서비스
- 시나리오 기반 학습으로 경각심을 높이는 예방 서비스

#### ④ 온라인 환등을 분석해 위험 상황을 사전 예측하는 개인 맞춤형 보안 코치
- 온라인 활동을 분석하여 위험 상황을 사전 예측

#### ⑤ 메체서·링크의 진위 여부를 실시간 검증해주는 개인 보안 어시스턴트
- 메시지와 링크의 진위 여부를 실시간 검증

---

## 🔍 참고 데이터 소스 (자체 수집 필요)

### 1. **AI-Hub** (https://www.aihub.or.kr)
- 현재 "피싱" 또는 "스미싱" 키워드로 검색 시 관련 데이터셋 **없음**
- 한국어 데이터셋: 908개 (다른 분야)
- **결론**: AI-Hub에는 피싱 관련 공개 데이터셋이 없습니다

### 2. **국내 정부 기관 데이터**

#### KISA (한국인터넷진흥원)
- **보호나라** (https://www.boho.or.kr/)
  - 스미싱/피싱 신고 센터
  - 실시간 사이버 위협 정보
  
- **KISA 스팸 신고** (https://spam.kisa.or.kr/)
  - 스팸/스미싱 문자 신고 시스템
  - 신고된 번호 조회 가능

#### 금융위원회 (https://www.fsc.go.kr/)
- 금융 사기 관련 공지사항
- 보이스피싱 예방 캠페인 자료

#### 경찰청 사이버안전국
- 사이버 범죄 신고 시스템
- 피싱 사례 공개 자료

### 3. **해외 공개 데이터셋**

#### Kaggle
- SMS Spam Collection Dataset
- Phishing Website Detection Dataset
- Email Spam Classification Dataset

#### UCI Machine Learning Repository
- SMS Spam Collection
- Phishing Websites Data Set

#### Hugging Face Datasets
- SMS Spam Dataset
- Phishing Email Dataset

#### GitHub
- 다양한 피싱 탐지 프로젝트 및 데이터셋

---

## 💡 데이터 수집 전략 (한국인 전용 서비스)

### 1. **직접 수집 방법**

#### A. 웹 크롤링
- **보호나라**: 실시간 사이버 위협 정보
- **금융위원회 공지**: 최신 보이스피싱 사례
- **뉴스 기사**: 피싱 관련 최신 사례 및 트렌드

#### B. 신고 데이터 API 활용
- KISA 스팸 신고 데이터 (공개 API 확인 필요)
- 스미싱 URL 블랙리스트 데이터

#### C. 커뮤니티 데이터
- 보이스피싱 피해 사례 게시판
- SNS 해시태그 (#스미싱, #보이스피싱, #피싱)

### 2. **데이터 증강 (Data Augmentation)**
- 실제 사례를 기반으로 변형 데이터 생성
- LLM을 활용한 합성 데이터 생성
  - ChatGPT/Claude를 활용해 피싱 메시지 패턴 생성
  - 정상 메시지와 피싱 메시지 생성

### 3. **라벨링 전략**
- **2단계 라벨링**:
  - 1차: 피싱(1) vs 정상(0)
  - 2차: 피싱 유형 (기관사칭, 지인사칭, 투자사기, 택배사칭 등)
  
- **추가 메타데이터**:
  - URL 포함 여부
  - 금전 요구 여부
  - 긴급성 표현 여부
  - 개인정보 요청 여부

### 4. **최소 데이터셋 목표 (MVP 기준)**
- **피싱 메시지**: 2,000 ~ 5,000건
- **정상 메시지**: 2,000 ~ 5,000건
- **총합**: 4,000 ~ 10,000건

---

## 🛠️ 권장 기술 스택

### Frontend
- **모바일**: Flutter / React Native
- **웹**: React / Vue.js / Next.js

### Backend
- **API**: FastAPI / Express.js / Spring Boot
- **Database**: PostgreSQL / MongoDB / Supabase

### AI/ML
- **텍스트 분석**: 
  - 한국어 NLP: KoBERT, KoELECTRA
  - Embedding: sentence-transformers
- **분류 모델**: 
  - LightGBM / XGBoost
  - Random Forest
- **LLM**: 
  - OpenAI GPT-4 API
  - Anthropic Claude API
  - 로컬 LLM: Ollama (Llama 3.1)

### DevOps
- **배포**: Vercel / AWS / GCP
- **컨테이너**: Docker / Docker Compose
- **CI/CD**: GitHub Actions

---

## 📝 제출 형식

대회 공식 페이지에서 확인 필요:
- MVP 프로토타입
- 서비스 기획서
- 발표 자료

---

## 🎯 다음 단계

1. **데이터 수집 시작**
   - KISA 보호나라 크롤링
   - Kaggle 데이터셋 다운로드
   - LLM으로 합성 데이터 생성

2. **MVP 개발**
   - 아이디어 구체화
   - 기술 스택 확정
   - 프로토타입 개발

3. **테스트 및 개선**
   - 실제 사용자 테스트
   - 피드백 반영
   - 최종 발표 자료 작성

---

## 📚 참고 링크

- [Dacon 대회 페이지](https://dacon.io/competitions/official/236666/overview/description)
- [KISA 보호나라](https://www.boho.or.kr/)
- [KISA 스팸신고](https://spam.kisa.or.kr/)
- [금융위원회](https://www.fsc.go.kr/)
- [Kaggle Phishing Datasets](https://www.kaggle.com/search?q=phishing)
