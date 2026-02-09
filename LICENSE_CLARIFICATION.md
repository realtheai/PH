# ⚖️ 라이선스 "불명" 의미와 대응 방법

## 🚨 **핵심 요약**

### ❌ **잘못된 생각**
```
"LICENSE 파일 없음 = 자유롭게 사용 가능"  ❌❌❌
```

### ✅ **올바른 이해**
```
LICENSE 파일 없음 = 기본 저작권 적용
                 = 저작자 허락 없이 사용 시 저작권 침해
```

---

## 📋 **한국 저작권법 기초**

### 1. **저작권 자동 발생**
```
저작물 창작 → 즉시 저작권 발생 (등록 불필요)
```

### 2. **저작자의 권리**
- 복제권
- 배포권
- 2차적 저작물 작성권
- **모든 권리는 기본적으로 저작자에게 귀속**

### 3. **타인이 사용하려면**
- 저작자의 **명시적 허락** 필요
- 라이선스 없음 = 허락 없음

---

## 🔍 **KOR_phishing 데이터셋 분석**

### 현황
```yaml
리포지토리: https://github.com/Ez-Sy01/KOR_phishing_Detect-Dataset
LICENSE 파일: ❌ 없음
저자: Siyoon Kim, JeongMin Park, Hyun Ahn, Yonggeol Lee*
소속: 한신대학교 (Hanshin University)
출처: 학술 논문 (MDPI Information, 2024)
인용 정보: 있음 (README에 명시)
```

### 법적 상태
```
✅ 저작권: 존재 (자동 발생)
❌ 사용 허락: 명시 없음
⚠️ 위험도: 높음 (특히 대회/상업적 사용)
```

---

## ⚖️ **사용 가능 여부 판단**

### 🔴 **불가능 (명확)**
1. **상업적 이용**
   - 판매, 유료 서비스 등

2. **2차 저작물 작성 후 배포**
   - 데이터 가공 후 재배포

3. **저작자 표시 없이 사용**

### 🟡 **애매함 (주의 필요)**
1. **대회 출품**
   - 상금 있음 = 상업적?
   - 상금 없음 = 비상업적?
   - **대회 규정 확인 필요**

2. **연구 목적**
   - Fair Use 가능성
   - 하지만 명확한 기준 없음

### 🟢 **가능 (일반적)**
1. **개인 학습 목적**
   - 공개하지 않고 개인적으로 사용

---

## 🎯 **대회 사용 시 리스크**

### Dacon 대회의 경우

#### ⚠️ **리스크**
1. **저작권 침해 소지**
   ```
   대회 상금 있음 → 상업적 목적으로 해석 가능
   저자 허락 없음 → 저작권 침해
   ```

2. **대회 실격 가능성**
   ```
   대회 규정: "합법적 데이터만 사용"
   라이선스 문제 발견 → 실격 처리
   ```

3. **수상 후 문제 발생**
   ```
   저자 이의 제기 → 상금 반환
   법적 분쟁 가능성
   ```

---

## ✅ **안전한 대응 방법**

### 1️⃣ **저자에게 직접 문의** (최우선 추천)

#### 연락처 정보
```yaml
저자: Yonggeol Lee (교신저자*)
소속: 한신대학교 컴퓨팅인공지능학부
ORCID: https://orcid.org/0009-0003-2276-3156
추정 이메일: 
  - 대학 이메일 (한신대 홈페이지 확인)
  - GitHub Issue 등록
```

#### 이메일 템플릿
```
제목: Dacon 피싱 예방 대회 - KOR_phishing_Detect-Dataset 사용 문의

존경하는 이용걸 교수님,

안녕하세요.
저는 Dacon에서 진행 중인 "피싱·스캠 예방을 위한 서비스 개발 경진대회"에 
참가하고 있는 개발자입니다.

귀하의 연구팀이 공개하신 KOR_phishing_Detect-Dataset을 
RAG 기반 피싱 탐지 서비스 개발에 활용하고자 문의드립니다.

【사용 목적】
- Dacon 경진대회 출품작 개발
- RAG(Retrieval-Augmented Generation) 시스템의 학습 데이터
- 비상업적 연구 목적

【데이터 활용 방식】
- 피싱 메시지 패턴 학습
- Vector Database 구축
- 실시간 피싱 탐지 서비스 개발

【약속 사항】
✅ 데이터 출처 명시 (논문 인용 포함)
✅ 연구 목적 외 상업적 사용 제한
✅ 데이터 재배포 금지

대회 출품을 위해 해당 데이터셋을 사용해도 되는지 
허락 여부를 회신해 주시면 감사하겠습니다.

귀하의 훌륭한 연구에 감사드리며, 긍정적인 답변을 기다리겠습니다.

감사합니다.

[본인 이름]
[연락처]
[이메일]
```

### 2️⃣ **GitHub Issue 등록**

```
Title: Request for Dataset Usage Permission - Competition Entry

Hi,

I'm participating in the Dacon phishing prevention competition and would like 
to use your KOR_phishing_Detect-Dataset for developing a RAG-based phishing 
detection service.

Could you please clarify the license terms or grant permission for competition use?

I will:
- Cite your work properly
- Use it for non-commercial research only
- Not redistribute the dataset

Thank you for your excellent research!
```

### 3️⃣ **대회 운영진에게 문의**

```
Dacon 운영팀에게:
"라이선스가 명시되지 않은 GitHub 공개 데이터셋을 사용해도 되나요?"
```

---

## 📊 **대안 전략**

### Plan A: 안전 우선 (즉시 실행 가능)
```
사용 데이터:
✅ 구글 뉴스 (120건) - 공개 정보
✅ Kaggle 오픈 데이터
⏳ Voice_phising_KR - 저자 승인 후
❌ KOR_phishing - 보류
```

### Plan B: 병행 전략
```
1. 구글 뉴스로 MVP 개발 (즉시)
2. GitHub 저자에게 이메일 발송 (병행)
3. 승인 받으면 데이터 추가 (업그레이드)
```

### Plan C: 풀 스택 (승인 후)
```
승인 받은 데이터만 사용:
✅ 구글 뉴스 (120건)
✅ Voice_phising_KR (1,200건)
✅ KOR_phishing (52,590건) - 승인 시
= 총 53,910건
```

---

## ⏰ **타임라인 추천**

### Day 1 (오늘)
- [x] 라이선스 분석 완료
- [ ] 저자 이메일 발송 (KOR_phishing)
- [ ] 저자 이메일 발송 (Voice_phising_KR)
- [x] 구글 뉴스 데이터로 개발 시작

### Day 2-3
- [ ] 저자 답변 대기
- [ ] 구글 뉴스 데이터 전처리
- [ ] MVP Vector DB 구축

### Day 4-7
- [ ] 저자 승인 확인
- [ ] 승인된 데이터 추가
- [ ] 대규모 RAG 시스템 구축

---

## 💡 **결론**

### ⚠️ **"라이선스 불명 ≠ 사용 가능"**

```
LICENSE 파일 없음 → 기본 저작권 적용
                 → 저작자 허락 없이 사용 = 위험
                 → 대회 출품 시 더 위험
```

### ✅ **안전한 방법**

1. **저자에게 문의** (1~3일 소요)
2. **승인 받고 사용** (안전)
3. **승인 안 오면** 구글 뉴스만 사용 (120건)

### 🎯 **추천 액션**

```bash
# 1. 즉시 실행
✅ 구글 뉴스로 개발 시작 (안전)

# 2. 병행 실행
📧 GitHub 저자 이메일 발송

# 3. 승인 후
🚀 대규모 데이터 추가 (54K건)
```

---

## 📞 **저자 연락처 찾기**

### 방법 1: 한신대학교 홈페이지
```
https://www.hs.ac.kr
→ 교수진 검색
→ "이용걸" 교수 (컴퓨팅인공지능학부)
```

### 방법 2: ORCID
```
https://orcid.org/0009-0003-2276-3156
→ 연락처 정보 확인
```

### 방법 3: 논문 연락처
```
MDPI Information 논문
→ Corresponding Author 연락처
```

### 방법 4: GitHub Issue
```
https://github.com/Ez-Sy01/KOR_phishing_Detect-Dataset/issues
→ New Issue 등록
```

---

## 🏆 **최종 권장 사항**

### 지금 당장:
1. ✅ **구글 뉴스로 개발 시작** (안전)
2. 📧 **저자 이메일 발송** (병행)
3. ⏳ **승인 기다리면서 진행** (효율적)

### 절대 하지 말 것:
- ❌ "불명이니까 그냥 써도 되겠지" (위험)
- ❌ 허락 없이 대회 출품 (법적 리스크)
- ❌ 출처 표시 없이 사용 (저작권 침해)

---

**라이선스 문제는 나중에 큰 문제가 될 수 있습니다. 지금 조금 번거롭더라도 확실히 해두는 게 안전합니다!** ⚖️
