# 피싱 데이터 크롤링 스크립트

## 📁 폴더 구조
```
phishingapp/
├── data/
│   ├── raw/           # 크롤링한 원본 데이터 (JSON)
│   └── processed/     # 전처리된 데이터
├── scripts/
│   ├── crawl_kisa_spam.py   # KISA 불법스팸대응센터 크롤러
│   ├── crawl_kisa_boho.py   # KISA 보호나라 크롤러
│   └── main_crawler.py      # 통합 실행 스크립트
└── requirements.txt
```

## 🚀 사용 방법

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 개별 크롤러 실행

#### KISA 불법스팸대응센터 크롤링
```bash
python scripts/crawl_kisa_spam.py
```

#### KISA 보호나라 크롤링
```bash
python scripts/crawl_kisa_boho.py
```

### 3. 통합 크롤러 실행 (권장)
```bash
python scripts/main_crawler.py
```

## 📊 출력 형식

### JSON 데이터 구조
```json
{
  "id": "notice_1",
  "source": "KISA 불법스팸대응센터",
  "category": "공지사항",
  "title": "[주의] 쿠팡 사칭 스미싱 주의 권고",
  "date": "2025-12-09",
  "url": "https://spam.kisa.or.kr/...",
  "content": "최근 쿠팡을 사칭한 스미싱이 다수 발생...",
  "keywords": ["피싱", "스미싱", "쿠팡", "택배"],
  "crawled_at": "2026-01-30T12:00:00"
}
```

## 📝 수집 데이터

### KISA 불법스팸대응센터
- ✅ 공지사항 (피싱 주의 권고)
- ✅ 실시간 피싱 사례
- ✅ 키워드 자동 추출

### KISA 보호나라
- ✅ 보안공지
- ✅ 최신 위협 정보
- ✅ 피싱 관련 가이드

## ⚠️ 주의사항

1. **서버 부하 방지**: 각 요청 사이에 0.5~1초 대기 시간 설정됨
2. **저작권**: 수집된 데이터는 개인 학습 및 연구 목적으로만 사용
3. **에러 처리**: 네트워크 오류 시 자동으로 건너뛰고 계속 진행

## 🔄 다음 단계

1. ✅ 크롤링 스크립트 작성 완료
2. ⏳ 실행 및 데이터 확인
3. ⏳ 데이터 전처리 (청크 분할, 임베딩)
4. ⏳ Vector DB 설정 (Qdrant/Pinecone/Supabase)
5. ⏳ RAG 시스템 구축
