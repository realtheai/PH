# PRD – Phishingapp (Korean-Focused Scam Detection App)

## 1. Product Overview

Phishingapp은은 한국 사용자를 대상으로 문자(SMS), 카카오톡, 메신저 메시지에 포함된 피싱·스미싱·메신저 사기를 빠르게 탐지하고, 사용자가 금전 송금 또는 링크 클릭을 하기 전에 경고를 제공하는 모바일 앱이다.

MVP 단계에서는 **Share → App 검사 흐름**을 제공하며, Phase2에서는 **백그라운드(Accessibility 기반) 자동 감지**로 확장한다.

핵심 철학:

* 정확한 예방보다 **사용자 행동을 멈추게 하는 UX**가 우선
* 개인정보 최소 수집
* 한국 피싱 패턴에 특화

---

## 2. Goals

### MVP Goals

* 사용자가 메시지를 공유하면 피싱 위험도 점수와 근거를 제공
* URL/도메인 기반 위험 신호 감지
* 룰 기반 + 경량 로직으로 안정적인 판정
* SQLite 또는 JSON 기반 데이터 관리

### Phase2 Goals

* 백그라운드 자동 감지
* 온디바이스 우선 판정
* 필요 시만 서버 분석 요청

---



## 4. Target Users

* 스마트폰 보안에 취약한 일반 사용자
* 부모님 폰에 설치해주는 자녀

---

## 5. Core User Flows

### MVP

1. 사용자가 문자/카톡에서 메시지 선택
2. Share → Phishing Checker 선택
3. 앱 실행 → 분석 중 화면
4. 결과 화면(위험/안전)

### Phase2

1. 백그라운드 Accessibility 감지
2. 의심 메시지 발견
3. 오버레이 경고 또는 알림
4. 상세 결과 화면 진입

---

## 6. Feature List

### MVP

* 메시지 입력/붙여넣기
* 위험도 점수(0–100)
* 위험 근거 리스트
* 권장 행동(클릭하지 마세요, 통화 확인)
* 검사 내역 로컬 저장

### Phase2

* Accessibility Service
* 포그라운드 서비스
* 오버레이 경고

---

## 7. Detection Strategy

### 7.1 Rule-Based Engine (Primary)

예시 신호:

* 기관 사칭 키워드(국세청, 경찰청, 금융감독원, 은행)
* 긴급성(즉시, 긴급, 제한, 정지)
* 금전 요구(송금, 상품권, 계좌)
* URL 포함 여부

점수 예시:

* 기관사칭 + URL: +40
* 긴급성 + 금전요구: +40
* 단축URL: +20

### 7.2 URL/Domain Checks

* 단축 URL 확장
* 도메인 유사도(levenshtein)
* 허용 도메인 목록

### 7.3 LLM (Optional, Explanation Only)

* 판정에는 사용하지 않음
* 위험 이유 1~2문장 설명 생성

---

## 8. Data Strategy

### 8.1 Data Usage (MVP)

* 모델 파인튜닝 없음
* 룰 설계, 테스트셋, 유사 사례 템플릿용

### 8.2 Data Sources

* KISA, 경찰청, 금융감독원 사례 페이지
* 뉴스 기사 인용 문구
* 합성 템플릿 생성
* 정상 SMS 공개 데이터

### 8.3 Data Volume Target

* 피싱: 3k–5k
* 정상: 3k–5k

### 8.4 Dataset Format

```csv
id,text,label,type,contains_url,contains_money,contains_urgency
```

---

## 9. Database Strategy

### MVP

* SQLite 파일 1개 또는 JSON

Tables:

* templates(id, type, text)
* known_domains(domain, label)
* scan_stats(type, count)

### Future

* PostgreSQL

---

## 10. LLM Strategy

### MVP

* External API (OpenAI or equivalent)
* Explanation-only usage

### Phase3

* Open-source sLLM (Gemma/Phi)

---

## 11. Tech Stack

### Frontend

* Next.js 14 (App Router)
* Tailwind CSS
* Zustand
* Static Export

### Mobile Bridge

* Capacitor

### Android Native Layer

* Kotlin
* Share Intent Receiver
* (Phase2) Accessibility Service

### Backend

* FastAPI
* Python

### Database

* SQLite

---

## 12. API Endpoints

POST /analyze

```
{ "text": "..." }
```

Response

```
{ "score": 87,
  "risk_level": "high",
  "reasons": ["기관 사칭", "긴급성", "URL 포함"],
  "llm_explanation": "..." }
```

POST /unshorten

GET /domains

---

## 13. Privacy Principles

* 메시지 저장 안함(옵션)
* 분석 후 즉시 폐기
* Phase2 온디바이스 우선

---

## 14. Milestones

Week 1

* Dataset 수집/합성
* 룰 엔진

Week 2

* Share → App
* FastAPI 연동

Week 3

* UI 완성
* SQLite 연동

---

## 15. Success Metrics

* Test Recall > 0.85
* Share Flow 성공률 > 95%
* 평균 응답 시간 < 1.5s

---

## 16. Future Roadmap

* Accessibility 기반 자동 감지
* 온디바이스 모델
* 이미지 OCR

---

## 17. Repository / File Tree Structure

```
phishing-checker/
├── README.md
├── .gitignore
├── docker-compose.yml           # FastAPI + (optional) SQLite volume
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py              # FastAPI entry
│       ├── api/
│       │   └── analyze.py       # /analyze, /unshorten endpoints
│       ├── core/
│       │   ├── rule_engine.py   # keyword + pattern scoring
│       │   ├── url_checker.py   # unshorten, domain similarity
│       │   └── llm_client.py    # explanation-only LLM call
│       ├── data/
│       │   ├── rules.json
│       │   ├── domains.json
│       │   └── app.db           # SQLite
│       └── schemas/
│           └── analyze.py       # request/response models
│
├── frontend/
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx             # main input
│   │   ├── result/page.tsx
│   │   └── history/page.tsx
│   ├── components/
│   │   ├── InputBox.tsx
│   │   ├── RiskMeter.tsx
│   │   └── ReasonList.tsx
│   └── store/
│       └── useScanStore.ts
│
├── mobile/
│   └── capacitor/
│       ├── capacitor.config.ts
│       └── android/
│           └── app/
│               └── src/main/java/com/phishingchecker/
│                   ├── MainActivity.kt
│                   ├── ShareReceiver.kt
│                   └── WebBridge.kt
│
├── data/
│   ├── raw/
│   ├── cleaned/
│   ├── synthetic/
│   ├── train.csv
│   ├── valid.csv
│   └── test.csv
│
└── docs/
    ├── PRD.md
    └── dataset_strategy.md
```

---

End of PRD




## 폴더 구조
phishing-checker/
├─ README.md
├─ .gitignore
├─ .env.example
├─ docker-compose.yml                  # (선택) backend + sqlite 볼륨 / nginx 등
├─ docs/
│  ├─ PRD.md                           # (캔버스 PRD 복사본)
│  ├─ API.md                           # 엔드포인트/요청-응답 예시
│  ├─ DATA.md                          # 데이터 수집/정제/라이선스 기록
│  └─ SECURITY.md                      # 개인정보/로그 정책
│
├─ data/
│  ├─ datasets/
│  │  ├─ raw/
│  │  ├─ cleaned/
│  │  ├─ splits/
│  │  └─ metadata/
│  │     ├─ sources.md                 # 출처 URL, 수집일, 라이선스
│  │     └─ schema.md                  # CSV 컬럼 정의
│  ├─ rules/
│  │  ├─ rules.json                    # 룰/가중치
│  │  ├─ entities_ko.json              # 기관/은행/택배사/키워드 사전
│  │  ├─ domains_allow.json            # 공식 도메인 allowlist
│  │  └─ url_shorteners.json           # bit.ly 등 단축 도메인 목록
│  └─ app.db                           # (옵션) MVP SQLite 파일(로컬)
│
├─ backend/
│  ├─ pyproject.toml                   # 또는 requirements.txt
│  ├─ Dockerfile
│  ├─ alembic.ini                      # (선택) migrations
│  ├─ alembic/                         # (선택)
│  └─ src/
│     ├─ app/
│     │  ├─ __init__.py
│     │  ├─ main.py                    # FastAPI 엔트리
│     │  ├─ config.py                  # env/config 로딩
│     │  ├─ logging_conf.py            # 원문 로그 금지 설정
│     │  │
│     │  ├─ api/
│     │  │  ├─ __init__.py
│     │  │  └─ v1/
│     │  │     ├─ __init__.py
│     │  │     ├─ analyze.py           # POST /analyze
│     │  │     ├─ unshorten.py         # POST /unshorten
│     │  │     ├─ domains.py           # GET /domains
│     │  │     └─ health.py            # GET /health
│     │  │
│     │  ├─ core/
│     │  │  ├─ __init__.py
│     │  │  ├─ schemas.py              # Pydantic request/response
│     │  │  ├─ rule_engine.py          # 룰 점수 엔진
│     │  │  ├─ url_features.py         # URL 추출/단축해제/도메인 유사도
│     │  │  ├─ llm_client.py           # (옵션) LLM API 호출(설명 전용)
│     │  │  └─ privacy.py              # 마스킹/익명화 유틸
│     │  │
│     │  ├─ storage/
│     │  │  ├─ __init__.py
│     │  │  ├─ sqlite.py               # SQLite 연결/쿼리
│     │  │  ├─ repo_templates.py       # 템플릿 조회
│     │  │  └─ repo_domains.py         # 도메인 목록 조회
│     │  │
│     │  ├─ scripts/
│     │  │  ├─ init_db.py              # SQLite 스키마 생성
│     │  │  ├─ import_templates.py     # data/rules → DB 적재
│     │  │  └─ import_domains.py
│     │  │
│     │  └─ tests/
│     │     ├─ test_rules.py
│     │     ├─ test_url_features.py
│     │     └─ test_api.py
│     │
│     └─ resources/
│        ├─ rules.json                 # 런타임 번들(또는 data/rules를 복사)
│        ├─ entities_ko.json
│        ├─ domains_allow.json
│        └─ url_shorteners.json
│
├─ frontend/
│  ├─ package.json
│  ├─ next.config.js                   # output: 'export'
│  ├─ tailwind.config.ts
│  ├─ postcss.config.js
│  ├─ tsconfig.json
│  ├─ public/
│  └─ src/
│     ├─ app/
│     │  ├─ layout.tsx
│     │  ├─ page.tsx                   # 메인 입력
│     │  ├─ loading.tsx                # 분석 중
│     │  ├─ result/
│     │  │  └─ page.tsx                # 결과 화면
│     │  ├─ history/
│     │  │  └─ page.tsx                # 검사 내역
│     │  └─ report/
│     │     └─ page.tsx                # 신고 안내/연결
│     │
│     ├─ components/
│     │  ├─ Header.tsx
│     │  ├─ RiskMeter.tsx
│     │  ├─ ReasonList.tsx
│     │  ├─ ActionButtons.tsx
│     │  └─ Toast.tsx
│     │
│     ├─ lib/
│     │  ├─ api.ts                     # backend 호출
│     │  ├─ validators.ts              # text/url 정규화
│     │  └─ constants.ts
│     │
│     ├─ store/
│     │  ├─ useScanStore.ts            # zustand (내역/설정)
│     │  └─ persist.ts                 # localStorage persist
│     │
│     └─ styles/
│        └─ globals.css
│
├─ mobile/
│  ├─ capacitor.config.ts
│  ├─ package.json                     # capacitor 의존성
│  ├─ android/
│  │  ├─ build.gradle
│  │  └─ app/
│  │     ├─ build.gradle
│  │     └─ src/main/
│  │        ├─ AndroidManifest.xml
│  │        ├─ java/com/yourapp/phishingchecker/
│  │        │  ├─ MainActivity.kt       # WebView/딥링크/브리지
│  │        │  ├─ ShareReceiverActivity.kt
│  │        │  ├─ DeepLinkRouter.kt
│  │        │  └─ bridge/
│  │        │     ├─ TextBridgePlugin.kt # (옵션) JS bridge
│  │        │     └─ SecureStorage.kt    # (옵션) Encrypted 저장
│  │        └─ res/
│  │           ├─ values/
│  │           └─ drawable/
│  │
│  └─ plugins/                          # 커스텀 capacitor plugins
│     └─ share-receiver/
│        ├─ README.md
│        ├─ src/
│        └─ android/
│
└─ tools/
   ├─ data_collect/
   │  ├─ collect_links.md              # 수집 대상 URL 목록(기관/뉴스)
   │  ├─ scrape_kisa.py                # (선택) 스크래핑
   │  ├─ scrape_news.py                # (선택)
   │  └─ sanitize.py                   # 개인정보 마스킹/정제
   ├─ data_generate/
   │  ├─ templates_ko.yaml             # 합성 템플릿
   │  ├─ slots_ko.yaml                 # 슬롯 사전
   │  └─ generate_synthetic.py         # 합성 데이터 생성
   └─ eval/
      ├─ split_dataset.py
      ├─ evaluate_rules.py             # 룰 엔진 Precision/Recall
      └─ report_metrics.py

mobile/
└─ android/
   └─ app/
      └─ src/
         └─ main/
            ├─ AndroidManifest.xml
            │  # Phase2 핵심: AccessibilityService/ForegroundService/Overlay 권한 및 서비스 등록
            │
            ├─ java/com/yourapp/phishingchecker/
            │  ├─ MainActivity.kt
            │  │  # Capacitor WebView 호스트(Next.js UI). 딥링크/라우팅 처리
            │  │
            │  ├─ ShareReceiverActivity.kt
            │  │  # Share Intent(ACTION_SEND) 수신 → 텍스트 추출 → 앱 화면으로 전달
            │  │
            │  ├─ DeepLinkRouter.kt
            │  │  # app://scan?source=... 형태의 딥링크를 WebView 라우트로 변환
            │  │
            │  ├─ bridge/
            │  │  ├─ TextBridgePlugin.kt
            │  │  │  # (옵션) JS ↔ Kotlin 브리지. 감지 텍스트/결과를 Web UI로 전달
            │  │  ├─ SecureStorage.kt
            │  │  │  # (옵션) EncryptedSharedPreferences 래퍼(검사내역/설정 로컬 저장)
            │  │  └─ WebEventBus.kt
            │  │     # (권장) 네이티브 이벤트(감지/경고)를 WebView로 푸시하는 단일 통로
            │  │
            │  ├─ accessibility/                         # ✅ Phase2 폴더(백그라운드 자동 감지)
            │  │  ├─ PhishingAccessibilityService.kt
            │  │  │  # AccessibilityService 엔트리\n            │  │  │  # - 화면 텍스트/노드 변경 이벤트 수신\n            │  │  │  # - 카톡/문자 등 대상 앱 필터링\n            │  │  │  # - 후보 텍스트를 Detector로 전달\n            │  │  │
            │  │  ├─ AccessibilityConfig.kt
            │  │  │  # 감지 대상 패키지/이벤트 타입/디바운스(ms) 등 설정\n            │  │  │  # 예: allowedPackages=[com.kakao.talk, com.android.mms]\n            │  │  │
            │  │  ├─ AccessibilityTextExtractor.kt
            │  │  │  # AccessibilityNodeInfo 트리에서 텍스트 추출\n            │  │  │  # - 중복 제거\n            │  │  │  # - 너무 긴 텍스트 컷\n            │  │  │  # - 입력창/대화창 구분(가능하면)\n            │  │  │
            │  │  ├─ AccessibilityEventFilter.kt
            │  │  │  # 이벤트 필터/스팸 방지\n            │  │  │  # - TYPE_WINDOW_CONTENT_CHANGED 등 고빈도 이벤트 디바운스\n            │  │  │  # - 동일 텍스트 반복 감지 차단\n            │  │  │  # - 특정 뷰(광고/시스템 UI) 제외\n            │  │  │
            │  │  ├─ TargetAppRegistry.kt
            │  │  │  # 대상 앱 목록/규칙\n            │  │  │  # - 카카오톡/문자/텔레그램 등\n            │  │  │  # - 앱별 화면 구조 차이를 흡수하기 위한 설정(옵션)\n            │  │  │
            │  │  ├─ BackgroundMonitorService.kt
            │  │  │  # Foreground Service(상태바 고정 알림)\n            │  │  │  # - OS 강제 종료 방지용\n            │  │  │  # - “보호 모드 실행 중” 지속 알림 제공\n            │  │  │
            │  │  ├─ monitor/
            │  │  │  ├─ MonitorController.kt
            │  │  │  │  # 보호 모드 ON/OFF 총괄\n            │  │  │  │  # - Accessibility 활성 여부 체크\n            │  │  │  │  # - Foreground Service 시작/종료\n            │  │  │  │  # - 설정 변경 반영\n            │  │  │  │
            │  │  │  ├─ MonitorState.kt
            │  │  │  │  # 현재 상태 모델\n            │  │  │  │  # - RUNNING/PAUSED/STOPPED\n            │  │  │  │  # - lastDetectedAt, lastPackage 등\n            │  │  │  │
            │  │  │  └─ MonitorScheduler.kt
            │  │  │     # (옵션) WorkManager/Alarm 등으로 상태 복구/정리 작업\n            │  │  │
            │  │  ├─ detection/
            │  │  │  ├─ Detector.kt
            │  │  │  │  # 감지 파이프라인 진입점\n            │  │  │  │  # - 룰 엔진(로컬) 1차 스코어\n            │  │  │  │  # - 의심일 때만 서버 분석 요청(옵션)\n            │  │  │  │  # - 결과를 Notifier로 전달\n            │  │  │  │
            │  │  │  ├─ RuleEngineLocal.kt
            │  │  │  │  # 로컬 룰 엔진(초경량)\n            │  │  │  │  # - 키워드/패턴 점수\n            │  │  │  │  # - URL 포함 여부, 단축URL 여부\n            │  │  │  │  # ※ 배터리/발열 때문에 LLM 상시 호출 금지\n            │  │  │  │
            │  │  │  ├─ UrlFeatureExtractor.kt
            │  │  │  │  # 텍스트에서 URL 추출 및 기본 특성\n            │  │  │  │  # - shortener 여부(bit.ly 등)\n            │  │  │  │  # - 도메인 정규화\n            │  │  │  │
            │  │  │  ├─ ServerAnalyzerClient.kt
            │  │  │  │  # (옵션) FastAPI /analyze 호출\n            │  │  │  │  # - 네트워크 실패 시 로컬 결과로 fallback\n            │  │  │  │
            │  │  │  ├─ DetectionModels.kt
            │  │  │  │  # DetectionResult/Reason/Score 등 공통 모델\n            │  │  │  │
            │  │  │  └─ DecisionPolicy.kt
            │  │  │     # 최종 판정 정책\n            │  │  │     # - score>=80: HIGH\n            │  │  │     # - 50~79: MEDIUM\n            │  │  │     # - else: LOW\n            │  │  │
            │  │  ├─ notify/
            │  │  │  ├─ Notifier.kt
            │  │  │  │  # 사용자 경고 출력 통합(알림/오버레이)\n            │  │  │  │
            │  │  │  ├─ NotificationChannelFactory.kt
            │  │  │  │  # 알림 채널 생성(보호모드/경고/결과)\n            │  │  │  │
            │  │  │  ├─ RiskNotificationBuilder.kt
            │  │  │  │  # Heads-up 알림 생성\n            │  │  │  │  # - “의심 메시지 감지”\n            │  │  │  │  # - ‘자세히 보기’ 액션(딥링크)\n            │  │  │  │
            │  │  │  └─ OverlayController.kt
            │  │  │     # (옵션) 오버레이 토스트/배너\n            │  │  │     # - SYSTEM_ALERT_WINDOW 또는 접근성 오버레이 방식\n            │  │  │     # - UX: 키보드 상단/화면 상단 경고\n            │  │  │
            │  │  ├─ privacy/
            │  │  │  ├─ TextSanitizer.kt
            │  │  │  │  # 개인정보 마스킹\n            │  │  │  │  # - 전화번호 → [PHONE]\n            │  │  │  │  # - 계좌번호 → [ACCOUNT]\n            │  │  │  │
            │  │  │  └─ DataRetentionPolicy.kt
            │  │  │     # 데이터 보관 정책\n            │  │  │     # - 원문 저장 기본 OFF\n            │  │  │     # - 최근 N개 요약/해시만 저장 옵션\n            │  │  │
            │  │  └─ settings/
            │  │     ├─ ProtectionSettings.kt
            │  │     │  # 보호 모드 설정 모델(ON/OFF, 대상 앱, 민감도)\n            │  │     ├─ SettingsRepository.kt
            │  │     │  # 설정 저장/로드(EncryptedSharedPreferences)\n            │  │     └─ AccessibilityPermissionHelper.kt
            │  │        # 접근성 권한 유도 UX\n            │  │        # - 설정 화면으로 이동 Intent\n            │  │        # - 활성 여부 확인\n            │  │
            │  └─ util/
            │     ├─ Debouncer.kt
            │     │  # 고빈도 이벤트 디바운싱 유틸\n            │     ├─ Hashing.kt
            │     │  # 텍스트 해시(중복 감지/원문 저장 회피)\n            │     └─ Time.kt
            │        # 시간/쿨다운 계산\n            │
            ├─ res/
            │  ├─ xml/
            │  │  ├─ accessibility_service_config.xml
            │  │  │  # AccessibilityService 설정 파일\n            │  │  │  # - eventTypes, feedbackType, flags 등\n            │  │  └─ file_paths.xml
            │  │     # (옵션) 공유/파일 핸들링\n            │  ├─ values/
            │  │  ├─ strings.xml
            │  │  │  # “보호 모드 실행 중” 등 사용자 문구\n            │  │  └─ colors.xml\n            │  └─ drawable/\n            │     # 알림 아이콘 등\n            │
            └─ assets/
               ├─ rules.json
               │  # 로컬 룰 엔진에서 사용하는 키워드/가중치\n               ├─ entities_ko.json
               │  # 기관/은행/택배사/키워드 사전\n               ├─ domains_allow.json
               │  # 공식 도메인 allowlist\n               └─ url_shorteners.json
                  # 단축 URL 도메인 목록\n```

원하면 다음도 같이 적어줄게(Phase2 구현에 바로 필요함):
- `AndroidManifest.xml`에 들어갈 **서비스/권한 선언 목록** 주석 포함 템플릿  
- `accessibility_service_config.xml` 예시(이벤트 타입/플래그 추천값)

