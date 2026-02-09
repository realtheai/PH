# 🎨 멀티모달 RAG 시스템 계획

## 🎯 **전략: 라이선스 안전 + 텍스트 + 이미지**

---

## 📊 **데이터 수집 계획**

### **Phase 1: 1년치 텍스트 데이터** (예상 3~5일)

```
네이버 API (1년):     ~12,000건
  ├─ 월별 키워드 검색 (12개월)
  ├─ 키워드: 피싱, 스미싱, 보이스피싱 등
  └─ API 무료 한도: 25,000건/일

구글 뉴스 (1년):      ~1,500건
  ├─ 한국어 피싱 뉴스
  └─ 날짜 필터링

Reddit (1년):         ~1,500건
  ├─ r/Scams, r/phishing 등
  └─ Top posts from past year

해외 뉴스 (1년):      ~500건
  ├─ Bing News
  └─ 영어 피싱 뉴스
━━━━━━━━━━━━━━━━━━━━━━━━
총 예상: 15,500건
```

### **Phase 2: 이미지 데이터** (예상 1~2일)

```
구글 이미지:          ~2,000개
  ├─ 스미싱 문자 스크린샷
  ├─ 피싱 메시지 예시
  ├─ 보이스피싱 수법 이미지
  └─ 금융사기 안내 포스터
━━━━━━━━━━━━━━━━━━━━━━━━
총 예상: 2,000개 이미지
```

---

## 🏗️ **멀티모달 RAG 아키텍처**

```
┌─────────────────────────────────────────────────────────┐
│                   사용자 입력                             │
│  • 텍스트: "이 문자가 피싱인가요?"                         │
│  • 이미지: [문자 스크린샷 업로드]                          │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│              멀티모달 임베딩 생성                          │
│  ┌──────────────────┐    ┌──────────────────┐          │
│  │  텍스트 임베딩    │    │  이미지 임베딩    │          │
│  │  (OpenAI)        │    │  (CLIP)          │          │
│  │  3,072 차원      │    │  512 차원        │          │
│  └────────┬─────────┘    └────────┬─────────┘          │
│           └──────────┬─────────────┘                    │
│                      ▼                                   │
│           [통합 임베딩: 3,584 차원]                      │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│              Vector Database (Qdrant)                    │
│                                                          │
│  ┌──────────────────────────────────────────┐          │
│  │  텍스트 컬렉션 (15,500건)                 │          │
│  │  • 뉴스 기사                              │          │
│  │  • Reddit 게시물                          │          │
│  │  • 피싱 사례                              │          │
│  └──────────────┬───────────────────────────┘          │
│                 │                                        │
│  ┌──────────────────────────────────────────┐          │
│  │  이미지 컬렉션 (2,000개)                  │          │
│  │  • 스미싱 문자 이미지                     │          │
│  │  • 피싱 메시지 스크린샷                   │          │
│  │  • 사기 수법 이미지                       │          │
│  └──────────────┬───────────────────────────┘          │
│                 │                                        │
│                 ▼                                        │
│      [유사도 검색: 텍스트 + 이미지]                      │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│              GPT-4 Vision (멀티모달 LLM)                  │
│  • 텍스트 Context                                        │
│  • 이미지 Context                                        │
│  • 종합 판단                                             │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│                    판정 결과                              │
│  • 피싱 확률: 98%                                        │
│  • 유형: 택배 스미싱                                     │
│  • 유사 사례 (텍스트 3개 + 이미지 2개)                    │
│  • 대응 방법                                             │
└─────────────────────────────────────────────────────────┘
```

---

## 💻 **구현 단계**

### **Step 1: 1년치 데이터 수집** (3~5일)

```bash
# 1. 네이버 API (1년치)
python scripts/crawl_historical_data.py

# 예상 결과:
# - naver_api: 12,000건
# - google: 1,500건
# - reddit: 1,500건
# - 총: 15,500건
```

### **Step 2: 이미지 수집** (1~2일)

```bash
# 구글 이미지 크롤링
python scripts/crawl_google_images.py

# 예상 결과:
# - 2,000개 이미지
# - 저장 위치: data/images/phishing/
```

### **Step 3: 멀티모달 임베딩** (1일)

```python
# scripts/generate_multimodal_embeddings.py

from openai import OpenAI
from transformers import CLIPProcessor, CLIPModel
from PIL import Image

# 텍스트 임베딩
def embed_text(text):
    client = OpenAI()
    response = client.embeddings.create(
        model="text-embedding-3-large",
        input=text
    )
    return response.data[0].embedding  # 3,072 차원

# 이미지 임베딩 (CLIP)
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def embed_image(image_path):
    image = Image.open(image_path)
    inputs = clip_processor(images=image, return_tensors="pt")
    features = clip_model.get_image_features(**inputs)
    return features[0].detach().numpy()  # 512 차원
```

### **Step 4: Vector DB 구축** (1일)

```python
# scripts/setup_multimodal_vectordb.py

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

client = QdrantClient("localhost", port=6333)

# 1. 텍스트 컬렉션
client.create_collection(
    collection_name="phishing_text",
    vectors_config=VectorParams(
        size=3072,
        distance=Distance.COSINE
    )
)

# 2. 이미지 컬렉션
client.create_collection(
    collection_name="phishing_images",
    vectors_config=VectorParams(
        size=512,
        distance=Distance.COSINE
    )
)

# 3. 멀티모달 컬렉션 (통합)
client.create_collection(
    collection_name="phishing_multimodal",
    vectors_config=VectorParams(
        size=3584,  # 3072 + 512
        distance=Distance.COSINE
    )
)
```

### **Step 5: 멀티모달 RAG** (2~3일)

```python
# src/multimodal_rag.py

class MultimodalPhishingRAG:
    def analyze(self, text: str = None, image_path: str = None):
        """텍스트 또는 이미지 또는 둘 다 분석"""
        
        # 1. 임베딩 생성
        embeddings = []
        if text:
            text_emb = self.embed_text(text)
            embeddings.append(text_emb)
        if image_path:
            image_emb = self.embed_image(image_path)
            embeddings.append(image_emb)
        
        # 2. Vector DB 검색
        text_results = self.search_text(text_emb) if text else []
        image_results = self.search_images(image_emb) if image_path else []
        
        # 3. GPT-4 Vision으로 종합 판단
        result = self.llm_analyze(
            text=text,
            image=image_path,
            similar_texts=text_results,
            similar_images=image_results
        )
        
        return result
```

---

## 📊 **예상 데이터 규모**

### **최종 데이터셋**

```
텍스트 데이터:        15,500건
  ├─ 네이버 API:      12,000건
  ├─ 구글 뉴스:        1,500건
  ├─ Reddit:           1,500건
  └─ 해외 뉴스:          500건

이미지 데이터:         2,000개
  ├─ 스미싱 문자:      1,000개
  ├─ 피싱 메시지:        600개
  └─ 사기 수법:          400개
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
총 데이터:            17,500건
```

### **저장 용량 예상**

```
텍스트 JSON:         ~150MB
이미지 파일:         ~2GB (평균 1MB/이미지)
Vector DB:           ~1GB
━━━━━━━━━━━━━━━━━━━━━━━━
총 용량:             ~3.15GB
```

---

## 💰 **비용 예상**

### **데이터 수집 비용**

```
네이버 API:          무료 (25,000건/일)
구글 크롤링:         무료
Reddit API:          무료
이미지 크롤링:       무료
━━━━━━━━━━━━━━━━━━━━━━━━
총 수집 비용:        $0
```

### **임베딩 생성 비용**

```
텍스트 임베딩:
  - 15,500건 × ~500 tokens = 7.75M tokens
  - $0.13 / 1M tokens
  - 총: ~$1.00

이미지 임베딩 (CLIP):
  - 2,000개 × 로컬 실행
  - 총: $0 (무료)
━━━━━━━━━━━━━━━━━━━━━━━━
총 임베딩 비용:      ~$1.00
```

### **운영 비용 (월 1만 쿼리)**

```
임베딩:              $0.50
GPT-4 Vision:        $100~150
인프라:              $10~50
━━━━━━━━━━━━━━━━━━━━━━━━
월 운영 비용:        $110~200
```

---

## 🎯 **경쟁 우위**

### **1. 멀티모달**
```
✅ 텍스트만: 일반적
✅ 텍스트 + 이미지: 차별화! 🔥
```

### **2. 대량 실제 사례**
```
✅ 1년치 데이터 (15,500건)
✅ 실제 스미싱 이미지 (2,000개)
✅ 최신 트렌드 반영
```

### **3. 라이선스 안전**
```
✅ 100% 공개 데이터
✅ 대회 출품 문제 없음
✅ 상업화 가능
```

---

## 🚀 **타임라인**

```
Week 1: 데이터 수집
  Day 1-3: 1년치 텍스트 크롤링
  Day 4-5: 이미지 크롤링
  Day 6-7: 데이터 정제

Week 2: Vector DB 구축
  Day 8-9: 임베딩 생성
  Day 10-11: Qdrant 설정
  Day 12-14: 멀티모달 RAG 구현

Week 3: 서비스 개발
  Day 15-17: API 개발
  Day 18-19: UI 개발 (이미지 업로드 기능)
  Day 20-21: 테스트 & 최적화
```

---

## 💡 **즉시 시작 가능한 작업**

### **1. 1년치 데이터 수집**
```bash
python scripts/crawl_historical_data.py
# 예상 소요: 3~5시간
# 결과: 15,500건
```

### **2. 이미지 수집**
```bash
python scripts/crawl_google_images.py
# 예상 소요: 1~2시간
# 결과: 2,000개 이미지
```

---

## 🎊 **최종 제안**

### ✅ **제안하신 전략이 최적입니다!**

**이유:**
1. ✅ 라이선스 100% 안전
2. ✅ 대량 데이터 (17,500건)
3. ✅ 멀티모달 (차별화)
4. ✅ 실제 사례 중심
5. ✅ 비용 효율적 (~$1)

**지금 바로 시작하시겠습니까?** 🚀

```bash
# 1단계: 1년치 크롤링 시작
python scripts/crawl_historical_data.py
```
