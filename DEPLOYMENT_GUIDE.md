## 🚀 GitHub Actions 배포를 위한 모델 의존성 분석

### 현재 사용 중인 모델/서비스

| 구성요소 | 모델/서비스 | 타입 | 배포 시 필요 여부 |
|---------|------------|------|------------------|
| **LLM 분석** | GPT-4o-mini (OpenAI) | ☁️ 외부 API | ✅ **API 키만 필요** |
| **임베딩 (검색)** | BGE-M3 (Ollama) | 🖥️ 로컬 서버 | ⚠️ **서버 필요 (문제!)** |
| **URL 검사** | Google Safe Browsing | ☁️ 외부 API | ✅ **API 키만 필요** |
| **데이터베이스** | Supabase | ☁️ 클라우드 | ✅ **URL만 필요** |

### ⚠️ 문제: BGE-M3 (Ollama)

**네, BGE-M3는 로컬 Ollama 서버가 필요합니다.**

```python
# 현재 임베딩 코드 (embedder.py)
requests.post(
    "http://localhost:11434/api/embeddings",  # ← 로컬 Ollama 서버 필요!
    json={"model": "bge-m3:567m", "prompt": text}
)
```

### 🔧 해결 방안

#### 옵션 1: OpenAI 임베딩으로 전환 (추천 ⭐)

**장점:**
- 서버 불필요, API 키만 있으면 됨
- GitHub Actions에서 바로 배포 가능
- 안정적이고 빠름

**단점:**
- DB 데이터를 OpenAI 임베딩으로 재생성 필요 (1,373개)
- 약간의 비용 발생 (하지만 매우 저렴)

**예상 비용:**
```
OpenAI text-embedding-3-small
- 1,373개 × 평균 100 토큰 = 137,300 토큰
- 비용: $0.02 / 1M 토큰 = 약 $0.003 (3원!)
```

#### 옵션 2: 벡터 검색 비활성화

**장점:**
- 바로 배포 가능
- LLM + 룰 기반만으로도 작동

**단점:**
- 유사 사례 검색 불가
- 정확도 약간 하락

#### 옵션 3: Ollama를 Docker로 함께 배포

**장점:**
- 기존 데이터 활용 가능

**단점:**
- 복잡한 설정 필요
- 서버 리소스 많이 필요 (GPU 권장)
- GitHub Actions에서 어려움

---

## 💡 추천 방법: OpenAI 임베딩 전환

### 1단계: 임베딩 모듈 수정 (이미 준비된 코드)

```python
# embedder.py
from openai import OpenAI

class Embedder:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    def create_embedding(self, text: str):
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
```

### 2단계: DB 데이터 재임베딩

```bash
# 스크립트 실행 (약 10-15분 소요)
python scripts/reembed_with_openai.py
```

### 3단계: GitHub Actions 배포

```yaml
# .github/workflows/deploy.yml
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  GOOGLE_SAFE_BROWSING_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
  SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
  SUPABASE_ANON_KEY: ${{ secrets.SUPABASE_ANON_KEY }}

# Ollama 불필요! ✅
```

---

## 🎯 결론

**GitHub Actions 배포를 위해서는:**

1. ✅ **LLM (GPT-4o-mini)**: 이미 API 사용 중 - 문제 없음
2. ⚠️ **임베딩 (BGE-M3)**: OpenAI로 전환 필요
3. ✅ **URL 검사**: 이미 API 사용 중 - 문제 없음
4. ✅ **DB**: 이미 클라우드 - 문제 없음

**권장사항:**
- **OpenAI 임베딩으로 전환** (비용 극소, 배포 간단)
- 또는 **벡터 검색 임시 비활성화** (즉시 배포 가능)

어떤 방향으로 진행하시겠습니까?
1. OpenAI 임베딩으로 전환 (DB 재임베딩)
2. 벡터 검색 비활성화 (LLM + 룰만 사용)
3. 다른 방법
