"""
OpenAI 임베딩으로 벡터화 (data & images 통합)
"""
import os
import requests
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

class OpenAIEmbedder:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        self.headers = {
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json'
        }
    
    def create_embedding(self, text: str) -> list:
        """OpenAI 임베딩 생성 (1536차원)"""
        try:
            text = text[:8000]  # 길이 제한
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text,
                encoding_format="float"
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"   ⚠️  임베딩 생성 오류: {e}")
            return None
    
    def get_unembedded_news(self):
        """임베딩 안 된 뉴스 가져오기 (최근 2일)"""
        try:
            two_days_ago = (datetime.now() - timedelta(days=2)).isoformat()
            
            url = f"{self.supabase_url}/rest/v1/phishing_news"
            params = {
                'select': 'id,content,translated_content',
                'embedding': 'is.null',
                'crawled_at': f'gte.{two_days_ago}',
                'order': 'id.desc',
                'limit': '1000'
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            return response.json() if response.status_code == 200 else []
        except Exception as e:
            print(f"   ⚠️  데이터 조회 오류: {e}")
            return []
    
    def get_unembedded_images(self):
        """임베딩 안 된 이미지 가져오기 (최근 2일)"""
        try:
            two_days_ago = (datetime.now() - timedelta(days=2)).isoformat()
            
            url = f"{self.supabase_url}/rest/v1/phishing_images"
            params = {
                'select': 'id,extracted_text',
                'embedding': 'is.null',
                'crawled_at': f'gte.{two_days_ago}',
                'order': 'id.desc',
                'limit': '1000'
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            return response.json() if response.status_code == 200 else []
        except Exception as e:
            print(f"   ⚠️  데이터 조회 오류: {e}")
            return []
    
    def update_embedding(self, table: str, record_id: int, embedding: list) -> bool:
        """임베딩 업데이트"""
        try:
            url = f"{self.supabase_url}/rest/v1/{table}"
            params = {'id': f'eq.{record_id}'}
            data = {'embedding': embedding}
            
            response = requests.patch(url, headers=self.headers, params=params, json=data, timeout=10)
            return response.status_code in [200, 204]
        except Exception as e:
            print(f"   ⚠️  업데이트 오류: {e}")
            return False
    
    def process_news(self):
        """뉴스 임베딩 처리"""
        print("\n🧠 [News] 뉴스 임베딩 시작...")
        
        items = self.get_unembedded_news()
        total = len(items)
        
        if total == 0:
            print("   ℹ️  임베딩할 뉴스 없음")
            return 0
        
        print(f"   📊 총 {total}개 뉴스 처리 중...")
        
        success = 0
        for idx, item in enumerate(items, 1):
            try:
                # 번역본 우선, 없으면 원문
                text = item.get('translated_content') or item.get('content', '')
                
                if not text or len(text.strip()) < 10:
                    continue
                
                # 임베딩 생성
                embedding = self.create_embedding(text)
                if not embedding:
                    continue
                
                # DB 업데이트
                if self.update_embedding('phishing_news', item['id'], embedding):
                    success += 1
                    if idx % 10 == 0:
                        print(f"      [{idx}/{total}] 처리 중... ({success} 성공)")
                
            except Exception as e:
                print(f"   ⚠️  [{idx}] 오류: {e}")
                continue
        
        print(f"   ✅ 뉴스 완료: {success}/{total}개 성공")
        return success
    
    def process_images(self):
        """이미지 임베딩 처리"""
        print("\n🧠 [Images] 이미지 임베딩 시작...")
        
        items = self.get_unembedded_images()
        total = len(items)
        
        if total == 0:
            print("   ℹ️  임베딩할 이미지 없음")
            return 0
        
        print(f"   📊 총 {total}개 이미지 처리 중...")
        
        success = 0
        for idx, item in enumerate(items, 1):
            try:
                text = item.get('extracted_text', '')
                
                if not text or len(text.strip()) < 10:
                    continue
                
                # 임베딩 생성
                embedding = self.create_embedding(text)
                if not embedding:
                    continue
                
                # DB 업데이트
                if self.update_embedding('phishing_images', item['id'], embedding):
                    success += 1
                    if idx % 10 == 0:
                        print(f"      [{idx}/{total}] 처리 중... ({success} 성공)")
                
            except Exception as e:
                print(f"   ⚠️  [{idx}] 오류: {e}")
                continue
        
        print(f"   ✅ 이미지 완료: {success}/{total}개 성공")
        return success
    
    def run(self):
        """전체 임베딩 실행"""
        print("\n" + "="*60)
        print("🧠 OpenAI 임베딩 생성 시작")
        print("="*60)
        
        news_count = self.process_news()
        image_count = self.process_images()
        
        total = news_count + image_count
        
        print("\n" + "="*60)
        print(f"🎉 임베딩 완료!")
        print(f"   📰 뉴스: {news_count}개")
        print(f"   🖼️  이미지: {image_count}개")
        print(f"   📊 총: {total}개")
        print("="*60)
        
        return total

if __name__ == "__main__":
    embedder = OpenAIEmbedder()
    embedder.run()
