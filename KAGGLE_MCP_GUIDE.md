# Kaggle MCP 사용 가이드

## 🔑 **인증 정보 확인**

`.env` 파일에 Kaggle 인증 정보가 저장되어 있습니다:
- `KAGGLE_USERNAME=claire2508`
- `KAGGLE_KEY=fd56310ca9b062437d3ae7fe3d1738a3`

---

## 📦 **Kaggle MCP 개요**

Kaggle은 **MCP (Model Context Protocol) 서버**를 제공하여 AI 에이전트와 개발 워크플로우를 간소화합니다.

### **공식 서버**
- URL: `https://www.kaggle.com/mcp`

### **서드파티 구현** (추천)
- GitHub: `arrismo/kaggle-mcp`
- GitHub: `dexhunter/kaggle-mcp`

---

## 🛠️ **사용 가능한 MCP 도구**

### 1. **search_kaggle_datasets(query)**
- 설명: 쿼리와 일치하는 데이터셋 검색
- 반환: 상위 10개 결과 (메타데이터 포함)
- 예시: `search_kaggle_datasets("phishing sms")`

### 2. **download_kaggle_dataset(dataset_ref)**
- 설명: 특정 데이터셋 다운로드 및 압축 해제
- 형식: `username/dataset-slug`
- 예시: `download_kaggle_dataset("shashwatwork/phishing-dataset-for-machine-learning")`

### 3. **generate_eda_notebook(dataset_ref)**
- 설명: 탐색적 데이터 분석(EDA) 노트북 프롬프트 생성
- 예시: `generate_eda_notebook("shashwatwork/phishing-dataset-for-machine-learning")`

---

## ⚙️ **설정 방법**

### **방법 1: Python 스크립트에서 직접 사용**

#### Kaggle API 설치
```bash
pip install kaggle
```

#### 인증 설정
```python
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# Kaggle 인증 정보 설정
os.environ['KAGGLE_USERNAME'] = os.getenv('KAGGLE_USERNAME')
os.environ['KAGGLE_KEY'] = os.getenv('KAGGLE_KEY')
```

#### 데이터셋 검색
```python
from kaggle.api.kaggle_api_extended import KaggleApi

api = KaggleApi()
api.authenticate()

# 피싱 데이터셋 검색
datasets = api.dataset_list(search='phishing')
for dataset in datasets[:10]:
    print(f"{dataset.ref} - {dataset.title}")
```

#### 데이터셋 다운로드
```python
# 데이터셋 다운로드 (data/raw 폴더에)
api.dataset_download_files(
    'shashwatwork/phishing-dataset-for-machine-learning',
    path='data/raw/',
    unzip=True
)
```

---

### **방법 2: MCP 서버 설정 (Cursor/Claude Desktop)**

#### Cursor 설정
`~/.cursor/mcp_config.json` 또는 프로젝트 `.cursor/mcp.json`:

```json
{
  "kaggle": {
    "type": "http",
    "url": "https://www.kaggle.com/mcp",
    "headers": {
      "Authorization": "Bearer YOUR_KAGGLE_TOKEN"
    }
  }
}
```

#### 서드파티 MCP 서버 (arrismo/kaggle-mcp)
```json
{
  "kaggle-mcp": {
    "command": "npx",
    "args": ["-y", "kaggle-mcp"],
    "env": {
      "KAGGLE_USERNAME": "claire2508",
      "KAGGLE_KEY": "fd56310ca9b062437d3ae7fe3d1738a3"
    }
  }
}
```

---

## 🚀 **실전 사용 예시**

### **1. 피싱 데이터셋 검색**

```python
import os
from dotenv import load_dotenv
from kaggle.api.kaggle_api_extended import KaggleApi

# 인증
load_dotenv()
os.environ['KAGGLE_USERNAME'] = os.getenv('KAGGLE_USERNAME')
os.environ['KAGGLE_KEY'] = os.getenv('KAGGLE_KEY')

api = KaggleApi()
api.authenticate()

# 검색 키워드
keywords = ['phishing', 'smishing', 'spam sms', 'fraud text']

for keyword in keywords:
    print(f"\n{'='*60}")
    print(f"검색 키워드: {keyword}")
    print('='*60)
    
    datasets = api.dataset_list(search=keyword)
    
    for i, dataset in enumerate(datasets[:5], 1):
        print(f"\n{i}. {dataset.title}")
        print(f"   작성자: {dataset.ref}")
        print(f"   크기: {dataset.size}")
        print(f"   다운로드: {dataset.downloadCount}")
        print(f"   투표: {dataset.voteCount}")
```

### **2. 데이터셋 다운로드**

```python
# 추천 데이터셋 리스트
recommended_datasets = [
    'shashwatwork/phishing-dataset-for-machine-learning',
    'haozhang1579/crawling2024-phishing-dataset-1',
]

for dataset_ref in recommended_datasets:
    print(f"\n다운로드 중: {dataset_ref}")
    
    try:
        api.dataset_download_files(
            dataset_ref,
            path='data/raw/kaggle/',
            unzip=True,
            quiet=False
        )
        print(f"✅ 완료: {dataset_ref}")
    except Exception as e:
        print(f"❌ 실패: {dataset_ref} - {e}")
```

---

## 📊 **추천 Kaggle 피싱 데이터셋**

| 데이터셋 | Ref | 크기 | 품질 |
|---------|-----|------|------|
| Phishing Dataset for ML | `shashwatwork/phishing-dataset-for-machine-learning` | 대량 | ⭐⭐⭐⭐ |
| Crawling2024 Phishing | `haozhang1579/crawling2024-phishing-dataset-1` | 대량 | ⭐⭐⭐⭐ |
| SMS Spam Collection | `uciml/sms-spam-collection-dataset` | 중량 | ⭐⭐⭐⭐ |

---

## 🔧 **전체 워크플로우**

### **단계 1: 환경 설정**
```bash
conda activate phishingapp
pip install kaggle python-dotenv
```

### **단계 2: 데이터셋 검색 및 다운로드**
```python
# scripts/download_kaggle_datasets.py
import os
from dotenv import load_dotenv
from kaggle.api.kaggle_api_extended import KaggleApi

load_dotenv()
os.environ['KAGGLE_USERNAME'] = os.getenv('KAGGLE_USERNAME')
os.environ['KAGGLE_KEY'] = os.getenv('KAGGLE_KEY')

api = KaggleApi()
api.authenticate()

# 검색
datasets = api.dataset_list(search='phishing sms')
for dataset in datasets[:10]:
    print(f"{dataset.ref} - {dataset.title}")

# 다운로드
api.dataset_download_files(
    'shashwatwork/phishing-dataset-for-machine-learning',
    path='data/raw/kaggle/',
    unzip=True
)
```

### **단계 3: 데이터 검증**
```python
import pandas as pd
import glob

# 다운로드된 파일 확인
files = glob.glob('data/raw/kaggle/**/*.csv', recursive=True)
for file in files:
    print(f"\n파일: {file}")
    df = pd.read_csv(file)
    print(f"행 수: {len(df)}")
    print(f"열: {df.columns.tolist()}")
    print(df.head())
```

---

## 💡 **다음 단계**

1. ✅ **Kaggle API 스크립트 작성**
   - 피싱 데이터셋 검색
   - 자동 다운로드
   
2. **데이터 전처리**
   - CSV → JSON 변환
   - 영어 → 한국어 번역 (필요 시)
   
3. **데이터 통합**
   - Kaggle 데이터 + 네이버 뉴스 데이터
   - Vector DB 저장

---

## 🎯 **즉시 실행 가능**

지금 바로 `scripts/download_kaggle_datasets.py` 스크립트를 작성해서 실행할까요?
