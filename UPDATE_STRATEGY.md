# 📅 DB 업데이트 전략

## 🎯 **업데이트 주기 전략**

---

## 📊 **단계별 접근**

### **Phase 1: 초기 구축** (1주)
```
목표: 대량 과거 데이터 확보

크롤링 전략:
├─ 네이버 API: 1년치 (12,000건)
├─ 구글 뉴스: 1년치 (1,500건)
├─ Reddit: 1년치 (1,500건)
└─ 이미지: 2,000개

업데이트: 없음 (초기 수집만)
```

### **Phase 2: 운영 단계** (이후)
```
목표: 최신 데이터 유지

업데이트 주기 (추천):
├─ 네이버 API: 매일 (최신 뉴스 중요)
├─ 구글 뉴스: 매일 (글로벌 트렌드)
├─ Reddit: 주 2회 (커뮤니티 업데이트 느림)
└─ 이미지: 월 1회 (수법 변화 느림)
```

---

## ⚖️ **매일 업데이트 vs 주기적 업데이트**

### **옵션 A: 매일 업데이트** ✅

#### 장점:
```
✅ 최신 피싱 트렌드 즉시 반영
✅ 뉴스 속보 실시간 반영
✅ 서비스 경쟁력 향상
✅ "오늘의 피싱 주의보" 기능 가능
✅ 데이터 신선도 최고
```

#### 단점:
```
⚠️ API 비용 증가 (네이버 API는 무료지만 한도 있음)
⚠️ 서버 부하 (매일 크롤링)
⚠️ 중복 데이터 많을 수 있음
⚠️ 관리 필요 (에러 모니터링)
```

#### 비용:
```
네이버 API: 무료 (25,000건/일 한도)
OpenAI 임베딩: 
  - 매일 100건 × 30일 = 3,000건/월
  - ~$0.15/월
Vector DB 삽입: 무료 (Qdrant 로컬)
━━━━━━━━━━━━━━━━━━━━━━━━
월 추가 비용: ~$0.15 (무시 가능)
```

---

### **옵션 B: 주기적 업데이트** (주 1~2회)

#### 장점:
```
✅ 비용 절감
✅ 서버 부하 적음
✅ 관리 편함
✅ 충분한 신선도
```

#### 단점:
```
⚠️ 실시간성 떨어짐
⚠️ 속보 반영 느림
⚠️ 경쟁력 약화
```

---

## 💡 **최적 전략 (추천)**

### **하이브리드 접근**

```yaml
매일 업데이트 (중요도 높음):
  네이버 API:
    - 키워드: "피싱 주의보", "스미싱 사례", "보이스피싱 피해"
    - 개수: 최신 100건
    - 시간: 매일 오전 7시
    - 이유: 한국 최신 뉴스, 가장 중요

  구글 뉴스:
    - 키워드: "피싱", "스미싱"
    - 개수: 최신 50건
    - 시간: 매일 오전 8시
    - 이유: 글로벌 트렌드

주 2회 업데이트:
  Reddit:
    - 서브레딧: r/Scams, r/phishing
    - 개수: 최신 50건
    - 시간: 월/목 오전 9시
    - 이유: 커뮤니티는 업데이트 느림

월 1회 업데이트:
  구글 이미지:
    - 키워드: "스미싱 문자 사례"
    - 개수: 최신 100개
    - 시간: 매월 1일
    - 이유: 수법 변화 느림
```

---

## 📋 **개별 크롤러 스크립트**

### **1. 네이버 API (매일)**

```python
# scripts/daily_naver.py

from crawl_naver_api import NaverAPINewsCrawler
from datetime import datetime
import json

def daily_update():
    """매일 네이버 최신 뉴스 수집"""
    crawler = NaverAPINewsCrawler()
    
    keywords = [
        '피싱 주의보',
        '스미싱 사례',
        '보이스피싱 피해'
    ]
    
    all_results = []
    
    for keyword in keywords:
        # 최신 100건만
        results = crawler.search_news(keyword, display=100)
        all_results.extend(results)
    
    # 중복 제거
    unique_results = {}
    for r in all_results:
        url = r['url']
        if url not in unique_results:
            unique_results[url] = r
    
    final_results = list(unique_results.values())
    
    # 저장
    today = datetime.now().strftime('%Y%m%d')
    filename = f'data/raw/daily/naver_{today}.json'
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(final_results, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 네이버 매일 업데이트: {len(final_results)}건")
    return final_results

if __name__ == "__main__":
    daily_update()
```

### **2. 구글 뉴스 (매일)**

```python
# scripts/daily_google.py

from crawl_google_news import GoogleNewsCrawler
from datetime import datetime
import json

def daily_update():
    """매일 구글 최신 뉴스 수집"""
    crawler = GoogleNewsCrawler()
    
    keywords = ['피싱 사례', '스미싱 주의']
    
    all_results = []
    
    for keyword in keywords:
        results = crawler.search_news(keyword, max_results=50)
        all_results.extend(results)
    
    # 중복 제거
    unique_results = {}
    for r in all_results:
        url = r['url']
        if url and url not in unique_results:
            unique_results[url] = r
    
    final_results = list(unique_results.values())
    
    # 저장
    today = datetime.now().strftime('%Y%m%d')
    filename = f'data/raw/daily/google_{today}.json'
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(final_results, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 구글 매일 업데이트: {len(final_results)}건")
    return final_results

if __name__ == "__main__":
    daily_update()
```

### **3. Reddit (주 2회)**

```python
# scripts/weekly_reddit.py

from crawl_reddit import RedditPhishingCrawler
from datetime import datetime
import json

def weekly_update():
    """주 2회 Reddit 업데이트"""
    crawler = RedditPhishingCrawler()
    
    subreddits = ['Scams', 'phishing', 'cybersecurity']
    
    all_results = []
    
    for subreddit in subreddits:
        results = crawler.search_subreddit(subreddit, limit=50)
        all_results.extend(results)
    
    # 저장
    today = datetime.now().strftime('%Y%m%d')
    filename = f'data/raw/weekly/reddit_{today}.json'
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Reddit 주간 업데이트: {len(all_results)}건")
    return all_results

if __name__ == "__main__":
    weekly_update()
```

---

## ⏰ **Cron 스케줄링**

### **Linux/Mac (crontab)**

```bash
# crontab -e

# 매일 오전 7시: 네이버
0 7 * * * cd /home/realtheai/phishingapp && python scripts/daily_naver.py

# 매일 오전 8시: 구글
0 8 * * * cd /home/realtheai/phishingapp && python scripts/daily_google.py

# 월/목 오전 9시: Reddit (1=월, 4=목)
0 9 * * 1,4 cd /home/realtheai/phishingapp && python scripts/weekly_reddit.py

# 매월 1일 오전 10시: 이미지
0 10 1 * * cd /home/realtheai/phishingapp && python scripts/monthly_images.py
```

### **Windows (Task Scheduler)**

```powershell
# 매일 오전 7시: 네이버
schtasks /create /tn "Naver Daily" /tr "python C:\phishingapp\scripts\daily_naver.py" /sc daily /st 07:00

# 매일 오전 8시: 구글
schtasks /create /tn "Google Daily" /tr "python C:\phishingapp\scripts\daily_google.py" /sc daily /st 08:00
```

---

## 🔄 **DB 업데이트 로직**

```python
# scripts/update_vectordb.py

from qdrant_client import QdrantClient
from generate_embeddings import embed_text

def update_vectordb(new_data):
    """새 데이터를 Vector DB에 추가"""
    
    client = QdrantClient("localhost", port=6333)
    
    # 중복 확인 (URL 기준)
    existing_urls = set()
    # TODO: Qdrant에서 기존 URL 가져오기
    
    new_points = []
    
    for item in new_data:
        url = item.get('url', '')
        
        # 중복 체크
        if url in existing_urls:
            continue
        
        # 임베딩 생성
        text = item.get('title', '') + ' ' + item.get('content', '')
        embedding = embed_text(text)
        
        # Point 추가
        point = {
            "id": hash(url),
            "vector": embedding,
            "payload": item
        }
        new_points.append(point)
    
    # DB에 추가
    if new_points:
        client.upsert(
            collection_name="phishing_cases",
            points=new_points
        )
        print(f"✅ Vector DB 업데이트: {len(new_points)}건 추가")
    else:
        print(f"ℹ️ 새로운 데이터 없음")
```

---

## 📊 **비용 분석**

### **매일 업데이트 시**

```
네이버 API: 무료 (한도 내)
구글 크롤링: 무료

임베딩 (매일 150건):
  - 150건/일 × 30일 = 4,500건/월
  - 4.5M tokens (평균 1,000 tokens/건)
  - $0.13 / 1M tokens
  - 월: ~$0.60

━━━━━━━━━━━━━━━━━━━━━━━━
월 추가 비용: ~$0.60 (매우 저렴!)
```

### **주 1회 업데이트 시**

```
임베딩 (주 150건):
  - 150건/주 × 4주 = 600건/월
  - 월: ~$0.10

━━━━━━━━━━━━━━━━━━━━━━━━
월 추가 비용: ~$0.10
```

---

## 🎯 **최종 추천**

### ✅ **제 의견: 매일 업데이트 추천!**

**이유:**
1. ✅ **비용 무시 가능** (~$0.60/월)
2. ✅ **최신성 중요** (피싱은 트렌드가 빠름)
3. ✅ **경쟁력 향상** ("오늘의 피싱 주의보")
4. ✅ **사용자 신뢰** (최신 데이터 사용)
5. ✅ **기술적으로 가능** (API 한도 충분)

**단, 초기에는:**
```
Week 1: 1년치 과거 데이터 한번에 수집
Week 2~: 매일 업데이트 시작
```

---

## 💡 **실행 계획**

### **Phase 1: 초기 수집** (지금 당장)
```bash
# 1년치 네이버
python scripts/crawl_naver_api.py  # 수동 실행, 키워드별 1년치

# 1년치 구글
python scripts/crawl_google_news.py

# Reddit
python scripts/crawl_reddit.py
```

### **Phase 2: 매일 업데이트** (이후)
```bash
# Cron 설정
crontab -e

# 매일 오전 7시, 8시, 9시
0 7 * * * python /path/to/daily_naver.py
0 8 * * * python /path/to/daily_google.py
```

---

## 🤔 **귀하의 의견은?**

1. **매일 업데이트** (추천, 비용 $0.60/월)
2. **주 2회 업데이트** (절충안)
3. **주 1회 업데이트** (최소)

어떤 방식이 좋으실까요?
