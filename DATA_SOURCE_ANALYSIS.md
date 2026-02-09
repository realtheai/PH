# 실제 접근 가능한 피싱/스미싱 데이터 소스 분석

## 🔍 **조사 완료 (2026-01-30)**

---

## ✅ **1. GitHub 데이터셋**

### 1-1. KOR_phishing_Detect-Dataset
- **URL**: https://github.com/Ez-Sy01/KOR_phishing_Detect-Dataset
- **설명**: 한국어 피싱 메시지 분류 데이터셋
- **논문**: "Classification of Korean Phishing Messages using Biased Discriminant Analysis under Extreme Class Imbalance Problem"
- **업데이트**: 2024년 8월
- **Stars**: 1
- **품질**: ⭐⭐⭐ (학술 연구용, 소규모)
- **양**: ⚠️ **적음** (정확한 개수 미확인, data 폴더 존재)
- **다운로드**: 가능 (git clone)

### 1-2. Voice_phising_KR
- **URL**: https://github.com/Mathhwi/Voice_phising_KR
- **설명**: 한국어 보이스피싱 데이터셋
- **업데이트**: 2025년 12월
- **Stars**: 1
- **품질**: ⭐⭐ (최신, 음성 피싱)
- **양**: ⚠️ **미확인**
- **다운로드**: 가능

---

## ✅ **2. Kaggle 데이터셋**

### 2-1. Phishing Dataset for Machine Learning
- **URL**: https://www.kaggle.com/datasets/shashwatwork/phishing-dataset-for-machine-learning
- **품질**: ⭐⭐⭐⭐
- **언어**: **영어** (한국어 아님)
- **양**: ⚠️ **대량** (정확한 개수 미확인)
- **다운로드**: Kaggle API 필요

### 2-2. Crawling2024 Phishing Dataset
- **URL**: https://www.kaggle.com/datasets/haozhang1579/crawling2024-phishing-dataset-1
- **업데이트**: 2024년
- **품질**: ⭐⭐⭐⭐
- **언어**: **영어** (한국어 아님)
- **양**: ⚠️ **대량** (최신 2024년 크롤링)
- **다운로드**: Kaggle API 필요

---

## ✅ **3. IEEE DataPort**

### 3-1. Korean Voice Phishing Detection Dataset (KorCCVi v2)
- **URL**: https://ieee-dataport.org/documents/korean-voice-phishing-detection-dataset-multilingual-back-translation-and-smote
- **설명**: 한국어 음성 피싱 대화 텍스트 데이터셋
- **특징**:
  - ✅ **한국어 전용**
  - 음성 피싱 대화 전사 (Vishing)
  - 비음성 피싱 대화 포함
  - Back-translation (영어, 중국어, 일본어 경유) 증강
  - SMOTE 기법으로 불균형 데이터 해결
- **품질**: ⭐⭐⭐⭐⭐ (고품질, 증강 데이터 포함)
- **양**: ⭐⭐⭐ **중대량** (원본 + 증강 데이터)
- **다운로드**: IEEE 계정 필요

---

## ✅ **4. Sting9 Anti-Phishing Dataset**

### 4-1. Comprehensive Anti-Phishing Dataset
- **URL**: https://sting9.org/dataset
- **GitHub**: https://github.com/sting9org/
- **설명**: 세계에서 가장 포괄적인 안티피싱 데이터셋
- **내용**:
  - 피싱 이메일
  - 스미싱 텍스트
  - 스캠 메시지
- **업데이트**: **주간 업데이트** 🔥
- **품질**: ⭐⭐⭐⭐⭐ (지속 업데이트)
- **양**: ⭐⭐⭐⭐⭐ **대량**
- **언어**: **영어** (한국어 아님)
- **라이선스**: CC0 (Public Domain)
- **API**: REST API 제공
- **다운로드**: GitHub에서 무료

---

## ✅ **5. 네이버 뉴스 (실시간 크롤링)**

### 5-1. 네이버 뉴스 검색
- **URL**: https://search.naver.com/search.naver?where=news&query=피싱+스미싱
- **내용**: 실시간 피싱/스미싱 사례 뉴스
- **품질**: ⭐⭐⭐⭐ (실제 사례, 최신)
- **양**: ⭐⭐⭐⭐⭐ **매우 많음**
- **언어**: ✅ **한국어 전용**
- **업데이트**: **실시간**
- **크롤링**: 가능 (뉴스 기사 크롤링)

**주요 사례**:
- 쿠팡 사칭 피싱
- SKT 유심 해킹 관련 피싱
- 민생회복 쿠폰 사칭
- 국세청 세금 환급 사칭
- 택배 확인 스미싱
- 보이스피싱 사례

**예상 수집량**: 수백~수천 건

---

## ❌ **6. 접근 불가능한 소스**

### KISA 불법스팸대응센터
- **URL**: https://spam.kisa.or.kr
- **문제**: 직접 URL 접근 차단 ("잘못된 접근")
- **해결 방법**: 메인 페이지에서 공지사항 크롤링 (제한적)

### KISA 보호나라
- **URL**: https://www.boho.or.kr
- **문제**: 404 오류, 페이지 접근 불가
- **상태**: 사용 불가

### AI Hub
- **URL**: https://aihub.or.kr
- **문제**: 검색 결과 오류
- **상태**: 피싱 관련 데이터셋 없음

---

## 📊 **데이터 품질 및 양 종합 평가**

| 소스 | 언어 | 품질 | 양 | 접근성 | 추천도 |
|------|------|------|-----|--------|--------|
| **네이버 뉴스** | 🇰🇷 한국어 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ 쉬움 | ⭐⭐⭐⭐⭐ |
| **KorCCVi v2 (IEEE)** | 🇰🇷 한국어 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⚠️ 계정 필요 | ⭐⭐⭐⭐⭐ |
| **Sting9** | 🇺🇸 영어 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ 쉬움 | ⭐⭐⭐⭐ |
| **GitHub (KOR)** | 🇰🇷 한국어 | ⭐⭐⭐ | ⭐ | ✅ 쉬움 | ⭐⭐⭐ |
| **Kaggle** | 🇺🇸 영어 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⚠️ API 필요 | ⭐⭐⭐ |

---

## 🎯 **최종 추천: 데이터 수집 전략**

### ✅ **1순위: 네이버 뉴스 크롤링** (즉시 시작 가능)
- **장점**: 
  - 100% 한국어
  - 실제 최신 피싱 사례
  - 대량 데이터
  - 접근 쉬움
- **예상 수집량**: 500~2,000건
- **크롤링 소요 시간**: 1~2시간

### ✅ **2순위: KorCCVi v2 (IEEE DataPort)**
- **장점**:
  - 고품질 한국어 데이터
  - 증강 데이터 포함
  - 학술 연구용
- **단점**: IEEE 계정 필요
- **예상 수집량**: 수백 건 (원본) + 증강 데이터

### ✅ **3순위: Sting9 Dataset (영어 → 한국어 번역)**
- **장점**:
  - 초대량 데이터
  - 주간 업데이트
  - API 제공
- **단점**: 영어 데이터 (번역 필요)
- **예상 수집량**: 수천~수만 건

### ⚠️ **4순위: GitHub 한국어 데이터셋**
- **장점**: 즉시 다운로드 가능
- **단점**: 소량 데이터
- **예상 수집량**: 수십~수백 건

---

## 🚀 **즉시 실행 가능한 크롤링 스크립트**

다음 순서로 진행하는 것을 추천합니다:

1. ✅ **네이버 뉴스 크롤러** 작성 (Selenium)
   - 키워드: "피싱 주의", "스미싱 주의", "보이스피싱 사례"
   - 수집 항목: 제목, 본문, 날짜, 언론사
   - 예상 시간: 1~2시간

2. ✅ **GitHub 데이터셋 다운로드** (git clone)
   - KOR_phishing_Detect-Dataset
   - Voice_phising_KR

3. ✅ **Sting9 데이터셋 다운로드** (GitHub/API)
   - 영어 → 한국어 번역 (ChatGPT/Claude API)

---

## 💡 **결론**

**한국어 전용 서비스**를 위해서는:
1. **네이버 뉴스 크롤링**이 가장 현실적이고 효과적
2. 실제 사례 기반 데이터
3. 대량 수집 가능
4. 즉시 시작 가능

지금 바로 **네이버 뉴스 크롤러**를 작성할까요?
