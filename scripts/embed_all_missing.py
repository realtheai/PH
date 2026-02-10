"""
OpenAI 임베딩으로 전체 미완료 데이터 벡터화
(날짜 제한 없이 모든 미완료 임베딩 처리)
"""
import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

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
        """임베딩 안 된 뉴스 가져오기 (전체, 날짜 제한 없음)"""
        try:
            url = f"{self.supabase_url}/rest/v1/phishing_news"
            
            all_items = []
            offset = 0
            limit = 1000
            
            while True:
                params = {
                    'select': 'id,content,translated_content',
                    'embedding': 'is.null',
                    'order': 'id.desc',
                    'offset': offset,
                    'limit': limit
                }
                
                response = requests.get(url, headers=self.headers, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if len(data) == 0:
                        break
                    all_items.extend(data)
                    offset += limit
                    if len(data) < limit:
                        break
                else:
                    break
            
            return all_items
        except Exception as e:
            print(f"   ⚠️  데이터 조회 오류: {e}")
            return []
    
    def get_unembedded_images(self):
        """임베딩 안 된 이미지 가져오기 (전체, 날짜 제한 없음)"""
        try:
            url = f"{self.supabase_url}/rest/v1/phishing_images"
            
            all_items = []
            offset = 0
            limit = 1000
            
            while True:
                params = {
                    'select': 'id,extracted_text,translated_content,translated_text',
                    'embedding': 'is.null',
                    'order': 'id.desc',
                    'offset': offset,
                    'limit': limit
                }
                
                response = requests.get(url, headers=self.headers, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if len(data) == 0:
                        break
                    all_items.extend(data)
                    offset += limit
                    if len(data) < limit:
                        break
                else:
                    break
            
            return all_items
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
        print("   📊 미완료 뉴스 데이터 수집 중...")
        
        items = self.get_unembedded_news()
        total = len(items)
        
        if total == 0:
            print("   ✅ 임베딩할 뉴스 없음 (모두 완료!)")
            return 0
        
        print(f"   📊 총 {total:,}개 뉴스 처리 시작...\n")
        
        success = 0
        failed = 0
        no_text = 0
        
        for idx, item in enumerate(items, 1):
            try:
                # 번역본 우선, 없으면 원문
                text = item.get('translated_content') or item.get('content', '')
                
                if not text or len(text.strip()) < 10:
                    no_text += 1
                    failed += 1
                    continue
                
                # 임베딩 생성
                embedding = self.create_embedding(text)
                if not embedding:
                    failed += 1
                    continue
                
                # DB 업데이트
                if self.update_embedding('phishing_news', item['id'], embedding):
                    success += 1
                    if idx % 50 == 0:
                        print(f"      [{idx:,}/{total:,}] 진행: {idx/total*100:.1f}% (성공: {success:,}, 실패: {failed})")
                else:
                    failed += 1
                
            except Exception as e:
                print(f"   ⚠️  [{idx}] 오류: {e}")
                failed += 1
                continue
        
        print(f"\n   ✅ 뉴스 완료!")
        print(f"      성공: {success:,}/{total:,}개 ({success/total*100:.1f}%)" if total > 0 else "")
        print(f"      실패: {failed}개 (텍스트 없음: {no_text}개)")
        return success
    
    def process_images(self):
        """이미지 임베딩 처리"""
        print("\n🧠 [Images] 이미지 임베딩 시작...")
        print("   📊 미완료 이미지 데이터 수집 중...")
        
        items = self.get_unembedded_images()
        total = len(items)
        
        if total == 0:
            print("   ✅ 임베딩할 이미지 없음 (모두 완료!)")
            return 0
        
        print(f"   📊 총 {total:,}개 이미지 처리 시작...\n")
        
        success = 0
        failed = 0
        no_text = 0
        
        for idx, item in enumerate(items, 1):
            try:
                # 번역본 우선, 없으면 OCR 텍스트
                text = item.get('translated_content') or item.get('translated_text') or item.get('extracted_text', '')
                
                if not text or len(text.strip()) < 10:
                    no_text += 1
                    failed += 1
                    continue
                
                # 임베딩 생성
                embedding = self.create_embedding(text)
                if not embedding:
                    failed += 1
                    continue
                
                # DB 업데이트
                if self.update_embedding('phishing_images', item['id'], embedding):
                    success += 1
                    if idx % 50 == 0:
                        print(f"      [{idx:,}/{total:,}] 진행: {idx/total*100:.1f}% (성공: {success:,}, 실패: {failed})")
                else:
                    failed += 1
                
            except Exception as e:
                print(f"   ⚠️  [{idx}] 오류: {e}")
                failed += 1
                continue
        
        print(f"\n   ✅ 이미지 완료!")
        print(f"      성공: {success:,}/{total:,}개 ({success/total*100:.1f}%)" if total > 0 else "")
        print(f"      실패: {failed}개 (텍스트 없음: {no_text}개)")
        return success
    
    def run(self):
        """전체 임베딩 실행"""
        print("\n" + "="*80)
        print("🧠 OpenAI 임베딩 생성 시작 (전체 미완료 데이터)")
        print("="*80)
        
        news_count = self.process_news()
        image_count = self.process_images()
        
        total = news_count + image_count
        
        print("\n" + "="*80)
        print(f"🎉 임베딩 완료!")
        print(f"   📰 뉴스: {news_count:,}개")
        print(f"   🖼️  이미지: {image_count:,}개")
        print(f"   📊 총: {total:,}개")
        print("="*80 + "\n")
        
        return total

if __name__ == "__main__":
    embedder = OpenAIEmbedder()
    embedder.run()
