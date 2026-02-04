"""
자동 데이터 정제 + Supabase 업로드
"""
import os
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

class DataProcessor:
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
    def translate_text(self, text: str) -> str:
        """Gemini로 영어 텍스트 번역"""
        if not text or len(text) < 20:
            return text
        
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
            
            prompt = f"""다음 영어 텍스트를 한국어로 자연스럽게 번역해주세요:

{text[:1000]}

번역:"""
            
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            result_data = response.json()
            translated = result_data['candidates'][0]['content']['parts'][0]['text'].strip()
            return translated
            
        except Exception as e:
            print(f"   ⚠️ 번역 실패: {e}")
            return text
    
    def classify_content(self, title: str, content: str) -> str:
        """Gemini로 콘텐츠 분류"""
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
            
            prompt = f"""다음 뉴스 기사를 분류해주세요. 정확히 다음 3가지 중 하나만 답변하세요:
- REAL_CASE: 실제 피싱 사례, 피해 사례, 적발 사례
- NEWS: 피싱 예방 캠페인, 주의보, 일반 뉴스
- NOISE: 피싱과 무관한 내용, 광고

제목: {title}
내용: {content[:500]}

분류 (REAL_CASE/NEWS/NOISE만 답변):"""
            
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            response = requests.post(url, json=payload, timeout=20)
            response.raise_for_status()
            
            result_data = response.json()
            category = result_data['candidates'][0]['content']['parts'][0]['text'].strip()
            
            # 정규화
            if 'REAL_CASE' in category:
                return 'REAL_CASE'
            elif 'NEWS' in category:
                return 'NEWS'
            else:
                return 'NOISE'
                
        except Exception as e:
            print(f"   ⚠️ 분류 실패: {e}")
            # 기본값: 키워드 기반 간단 분류
            if any(kw in title + content for kw in ['피해', '사례', '적발', '검거', '당해']):
                return 'REAL_CASE'
            elif any(kw in title + content for kw in ['예방', '캠페인', '주의', '대응']):
                return 'NEWS'
            else:
                return 'NOISE'
    
    def process_naver_data(self, json_file: str) -> List[Dict]:
        """네이버 데이터 처리"""
        print(f"\n📰 네이버 데이터 처리: {json_file}")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        processed = []
        for idx, item in enumerate(data, 1):
            print(f"  [{idx}/{len(data)}] 처리 중...", end=' ')
            
            # 분류
            category = self.classify_content(item['title'], item['content'])
            
            processed_item = {
                'source': 'naver',
                'title': item['title'],
                'content': item['content'],
                'url': item['url'],
                'category': category,
                'phishing_type': None,  # TODO: 추후 구현
                'original_language': 'ko',
                'translated_content': None,
                'keywords': item.get('keywords', []),
                'content_length': item['content_length'],
                'published_at': item.get('published_at'),
                'crawled_at': item['crawled_at']
            }
            
            processed.append(processed_item)
            print(f"✅ ({category})")
        
        return processed
    
    def process_reddit_data(self, json_file: str) -> List[Dict]:
        """Reddit 데이터 처리 (영어 → 번역)"""
        print(f"\n🔴 Reddit 데이터 처리: {json_file}")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        processed = []
        for idx, item in enumerate(data, 1):
            print(f"  [{idx}/{len(data)}] 번역 중...", end=' ')
            
            # 번역
            translated_title = self.translate_text(item['title'])
            translated_content = self.translate_text(item['content'][:1000])
            
            # 분류
            category = self.classify_content(translated_title, translated_content)
            
            processed_item = {
                'source': 'reddit',
                'title': translated_title,
                'content': translated_content,
                'url': item['url'],
                'category': category,
                'phishing_type': None,
                'original_language': 'en',
                'translated_content': translated_content,
                'keywords': item.get('extracted_keywords', []),
                'content_length': len(item['content']),
                'published_at': datetime.fromtimestamp(item['created_utc']).isoformat(),
                'crawled_at': item['crawled_at']
            }
            
            processed.append(processed_item)
            print(f"✅ ({category})")
        
        return processed
    
    def upload_to_supabase(self, data: List[Dict], table: str = 'phishing_news'):
        """Supabase에 데이터 업로드"""
        print(f"\n💾 Supabase 업로드 중: {len(data)}건")
        
        success_count = 0
        duplicate_count = 0
        error_count = 0
        
        for idx, item in enumerate(data, 1):
            try:
                # URL 중복 체크
                existing = self.supabase.table(table).select("id").eq("url", item['url']).execute()
                
                if existing.data:
                    duplicate_count += 1
                    print(f"  [{idx}/{len(data)}] ⚠️  중복 (스킵)")
                    continue
                
                # INSERT
                self.supabase.table(table).insert(item).execute()
                success_count += 1
                print(f"  [{idx}/{len(data)}] ✅ 업로드")
                
            except Exception as e:
                error_count += 1
                print(f"  [{idx}/{len(data)}] ❌ 오류: {e}")
        
        print(f"\n📊 업로드 결과:")
        print(f"   성공: {success_count}건")
        print(f"   중복: {duplicate_count}건")
        print(f"   실패: {error_count}건")
        
        return success_count
    
    def update_stats(self, date: str, stats: Dict):
        """통계 업데이트"""
        try:
            self.supabase.table('phishing_stats').upsert({
                'stat_date': date,
                **stats
            }).execute()
            print(f"✅ 통계 업데이트 완료: {date}")
        except Exception as e:
            print(f"❌ 통계 업데이트 실패: {e}")

def main():
    print("="*60)
    print("🤖 자동 데이터 정제 + DB 업로드")
    print("="*60)
    
    processor = DataProcessor()
    
    today = datetime.now().strftime('%Y%m%d')
    
    # 1. 네이버 데이터 처리
    naver_file = f'data/raw/daily/naver_{today}.json'
    if os.path.exists(naver_file):
        naver_data = processor.process_naver_data(naver_file)
        naver_count = processor.upload_to_supabase(naver_data)
    else:
        naver_count = 0
        print(f"\n⚠️  네이버 데이터 없음: {naver_file}")
    
    # 2. 구글 데이터 처리 (동일한 로직)
    google_file = f'data/raw/daily/google_{today}.json'
    if os.path.exists(google_file):
        google_data = processor.process_naver_data(google_file)  # 한국어이므로 동일
        google_count = processor.upload_to_supabase(google_data)
    else:
        google_count = 0
        print(f"\n⚠️  구글 데이터 없음: {google_file}")
    
    # 3. Reddit 데이터 처리 (주 2회)
    reddit_file = f'data/raw/weekly/reddit_{today}.json'
    if os.path.exists(reddit_file):
        reddit_data = processor.process_reddit_data(reddit_file)
        reddit_count = processor.upload_to_supabase(reddit_data)
    else:
        reddit_count = 0
    
    # 4. 통계 업데이트
    stats = {
        'naver_count': naver_count,
        'google_count': google_count,
        'reddit_count': reddit_count
    }
    processor.update_stats(datetime.now().strftime('%Y-%m-%d'), stats)
    
    print("\n" + "="*60)
    print("✅ 자동화 완료!")
    print("="*60)

if __name__ == "__main__":
    main()
