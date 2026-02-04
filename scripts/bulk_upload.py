"""
1년치 데이터 대량 업로드
- Gemini로 분류 (선택적)
- URL 기반 중복 제거
- Batch 업로드
"""
import os
import json
import requests
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

class BulkUploader:
    def __init__(self, use_classification=False):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.use_classification = use_classification
        
    def classify_content(self, title: str, content: str) -> str:
        """Gemini로 콘텐츠 분류 (선택적)"""
        if not self.use_classification:
            # 기본 키워드 기반 분류
            text = title + " " + content
            if any(kw in text for kw in ['피해', '사례', '적발', '검거', '당해', '속아']):
                return 'REAL_CASE'
            elif any(kw in text for kw in ['예방', '캠페인', '주의', '대응', '경보']):
                return 'NEWS'
            else:
                return 'NEWS'  # 기본값
        
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
            
            prompt = f"""다음 뉴스를 분류하세요. REAL_CASE, NEWS, NOISE 중 하나만 답변:

제목: {title[:100]}
내용: {content[:300]}

분류:"""
            
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            result_data = response.json()
            category = result_data['candidates'][0]['content']['parts'][0]['text'].strip()
            
            if 'REAL_CASE' in category:
                return 'REAL_CASE'
            elif 'NEWS' in category:
                return 'NEWS'
            else:
                return 'NOISE'
                
        except Exception as e:
            print(f"   분류 오류: {e}")
            return 'NEWS'
    
    def process_naver_data(self, json_file: str) -> List[Dict]:
        """네이버 데이터 처리"""
        print(f"\n📰 네이버 데이터 처리: {json_file}")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"   전체: {len(data)}건")
        
        processed = []
        for idx, item in enumerate(data, 1):
            if idx % 100 == 0:
                print(f"   진행: {idx}/{len(data)} ({idx/len(data)*100:.1f}%)")
            
            category = self.classify_content(item['title'], item.get('content', ''))
            
            processed_item = {
                'source': 'naver',
                'title': item['title'],
                'content': item.get('content', ''),
                'url': item['url'],
                'category': category,
                'original_language': 'ko',
                'content_length': len(item.get('content', '')),
                'published_at': item.get('date'),
                'crawled_at': item['crawled_at']
            }
            
            processed.append(processed_item)
        
        print(f"   완료: {len(processed)}건 처리")
        return processed
    
    def process_google_data(self, json_file: str) -> List[Dict]:
        """구글 뉴스 데이터 처리"""
        print(f"\n🌐 구글 뉴스 데이터 처리: {json_file}")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"   전체: {len(data)}건")
        
        processed = []
        for idx, item in enumerate(data, 1):
            if idx % 100 == 0:
                print(f"   진행: {idx}/{len(data)} ({idx/len(data)*100:.1f}%)")
            
            category = self.classify_content(item['title'], item.get('content', ''))
            
            processed_item = {
                'source': 'google',
                'title': item['title'],
                'content': item.get('content', ''),
                'url': item['url'],
                'category': category,
                'original_language': 'ko',
                'content_length': len(item.get('content', '')),
                'published_at': item.get('published_at'),
                'crawled_at': item['crawled_at']
            }
            
            processed.append(processed_item)
        
        print(f"   완료: {len(processed)}건 처리")
        return processed
    
    def process_reddit_data(self, json_file: str) -> List[Dict]:
        """Reddit 데이터 처리 (영어)"""
        print(f"\n🔴 Reddit 데이터 처리: {json_file}")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"   전체: {len(data)}건")
        
        processed = []
        for idx, item in enumerate(data, 1):
            if idx % 50 == 0:
                print(f"   진행: {idx}/{len(data)} ({idx/len(data)*100:.1f}%)")
            
            # Reddit은 영어이므로 번역 없이 원문 저장
            processed_item = {
                'source': 'reddit',
                'title': item['title'],
                'content': item.get('content', ''),
                'url': item['url'],
                'category': 'NEWS',  # Reddit은 기본 NEWS
                'original_language': 'en',
                'content_length': len(item.get('content', '')),
                'published_at': datetime.fromtimestamp(item['created_utc']).isoformat() if 'created_utc' in item else None,
                'crawled_at': item['crawled_at']
            }
            
            processed.append(processed_item)
        
        print(f"   완료: {len(processed)}건 처리")
        return processed
    
    def upload_batch(self, data: List[Dict], batch_size: int = 100) -> Dict:
        """배치 업로드"""
        print(f"\n💾 Supabase 업로드 시작: {len(data)}건")
        
        success_count = 0
        duplicate_count = 0
        error_count = 0
        
        # 배치 단위로 업로드
        for i in range(0, len(data), batch_size):
            batch = data[i:i+batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(data) + batch_size - 1) // batch_size
            
            print(f"   배치 {batch_num}/{total_batches} 업로드 중...", end=' ')
            
            for item in batch:
                try:
                    # URL 중복 체크
                    existing = self.supabase.table('phishing_news')\
                        .select("id")\
                        .eq("url", item['url'])\
                        .execute()
                    
                    if existing.data:
                        duplicate_count += 1
                        continue
                    
                    # INSERT
                    self.supabase.table('phishing_news').insert(item).execute()
                    success_count += 1
                    
                except Exception as e:
                    error_count += 1
                    if error_count <= 5:  # 처음 5개 오류만 출력
                        print(f"\n   오류: {e}")
            
            print(f"✅ (성공: {success_count}, 중복: {duplicate_count}, 실패: {error_count})")
        
        return {
            'success': success_count,
            'duplicate': duplicate_count,
            'error': error_count
        }

def main():
    print("="*60)
    print("📦 1년치 데이터 대량 업로드")
    print("="*60)
    
    # 분류 사용 여부 선택 (False = 빠른 키워드 기반)
    uploader = BulkUploader(use_classification=False)
    
    total_stats = {
        'success': 0,
        'duplicate': 0,
        'error': 0
    }
    
    # 1. 네이버 데이터 (fixed 버전 사용)
    print("\n" + "="*60)
    print("1/3: 네이버 뉴스")
    print("="*60)
    naver_file = 'data/raw/naver_api_2025-02-01_to_2026-01-31_fixed.json'
    naver_data = uploader.process_naver_data(naver_file)
    naver_stats = uploader.upload_batch(naver_data)
    
    for key in total_stats:
        total_stats[key] += naver_stats[key]
    
    # 2. 구글 뉴스
    print("\n" + "="*60)
    print("2/3: 구글 뉴스")
    print("="*60)
    google_file = 'data/raw/google_news_2025-02-01_to_2026-01-31.json'
    google_data = uploader.process_google_data(google_file)
    google_stats = uploader.upload_batch(google_data)
    
    for key in total_stats:
        total_stats[key] += google_stats[key]
    
    # 3. Reddit
    print("\n" + "="*60)
    print("3/3: Reddit")
    print("="*60)
    reddit_file = 'data/raw/reddit_2025-02-01_to_2026-01-31.json'
    reddit_data = uploader.process_reddit_data(reddit_file)
    reddit_stats = uploader.upload_batch(reddit_data)
    
    for key in total_stats:
        total_stats[key] += reddit_stats[key]
    
    # 최종 결과
    print("\n" + "="*60)
    print("📊 최종 업로드 결과")
    print("="*60)
    print(f"✅ 성공: {total_stats['success']:,}건")
    print(f"⚠️  중복: {total_stats['duplicate']:,}건")
    print(f"❌ 실패: {total_stats['error']:,}건")
    print("="*60)
    
    # 통계 업데이트
    try:
        uploader.supabase.table('phishing_stats').upsert({
            'stat_date': datetime.now().strftime('%Y-%m-%d'),
            'naver_count': naver_stats['success'],
            'google_count': google_stats['success'],
            'reddit_count': reddit_stats['success'],
            'updated_at': datetime.now().isoformat()
        }).execute()
        print("✅ 통계 업데이트 완료")
    except Exception as e:
        print(f"⚠️  통계 업데이트 실패: {e}")

if __name__ == "__main__":
    main()
