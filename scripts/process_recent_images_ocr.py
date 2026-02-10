"""
최근 수집 이미지 OCR 처리 (DB 기반)
- 최근 2일 내 수집된 이미지
- OCR 안 된 이미지만 처리
"""
import os
import base64
import requests
from io import BytesIO
from PIL import Image
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time

load_dotenv()

class RecentImageOCR:
    def __init__(self):
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        self.headers = {
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json'
        }
        
        print("✅ OCR Processor 초기화 (OpenAI gpt-4o-mini)")
    
    def get_unprocessed_images(self):
        """OCR 안 된 최근 이미지 가져오기"""
        try:
            two_days_ago = (datetime.now() - timedelta(days=2)).isoformat()
            
            url = f"{self.supabase_url}/rest/v1/phishing_images"
            params = {
                'select': 'id,image_url',
                'crawled_at': f'gte.{two_days_ago}',
                'or': '(extracted_text.is.null,extracted_text.eq.)',
                'order': 'id.desc',
                'limit': '1000'
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ DB 조회 실패: {response.status_code}")
                return []
        
        except Exception as e:
            print(f"❌ DB 조회 오류: {e}")
            return []
    
    def download_image(self, url: str) -> bytes:
        """이미지 URL에서 다운로드"""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.content
            return None
        except:
            return None
    
    def extract_text_with_openai(self, image_data: bytes) -> dict:
        """OpenAI Vision으로 OCR"""
        try:
            # Base64 인코딩
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.openai_key}"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Extract all text from this image. Output only the text in original language (Korean/English)."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]
                    }],
                    "max_tokens": 1024,
                    "temperature": 0.1
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                text = result['choices'][0]['message']['content'].strip()
                return {'success': True, 'text': text}
            else:
                return {'success': False, 'error': f'HTTP {response.status_code}'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def update_extracted_text(self, record_id: int, text: str) -> bool:
        """OCR 결과 업데이트"""
        try:
            url = f"{self.supabase_url}/rest/v1/phishing_images"
            params = {'id': f'eq.{record_id}'}
            
            # 언어 감지
            korean_chars = sum(1 for c in text if '\uac00' <= c <= '\ud7a3')
            total_chars = len(text.replace(' ', '').replace('\n', ''))
            language = 'ko' if total_chars > 0 and korean_chars / total_chars > 0.3 else 'en'
            
            data = {
                'extracted_text': text[:5000],
                'original_language': language,
                'processed_at': datetime.now().isoformat()
            }
            
            response = requests.patch(url, headers=self.headers, params=params, json=data, timeout=10)
            return response.status_code in [200, 204]
        
        except Exception as e:
            print(f"   ⚠️  업데이트 오류: {e}")
            return False
    
    def process_all(self):
        """전체 처리"""
        print(f"\n{'='*60}")
        print(f"🔍 최근 이미지 OCR 처리 시작")
        print(f"{'='*60}\n")
        
        # 1. OCR 안 된 이미지 조회
        images = self.get_unprocessed_images()
        total = len(images)
        
        if total == 0:
            print("ℹ️  처리할 이미지 없음")
            return {'success': 0, 'failed': 0}
        
        print(f"📊 총 {total}개 이미지 처리 중...\n")
        
        success = 0
        failed = 0
        
        for idx, item in enumerate(images, 1):
            try:
                image_id = item['id']
                image_url = item['image_url']
                
                print(f"[{idx}/{total}] 📸 ID:{image_id}")
                
                # 2. 이미지 다운로드
                image_data = self.download_image(image_url)
                if not image_data:
                    print(f"   ❌ 다운로드 실패")
                    failed += 1
                    continue
                
                # 3. OCR
                result = self.extract_text_with_openai(image_data)
                if not result['success']:
                    print(f"   ❌ OCR 실패: {result.get('error')}")
                    failed += 1
                    time.sleep(1)
                    continue
                
                text = result['text']
                print(f"   ✅ OCR 성공: {len(text)}자")
                
                # 4. DB 업데이트
                if self.update_extracted_text(image_id, text):
                    print(f"   💾 DB 업데이트 완료")
                    success += 1
                else:
                    print(f"   ⚠️  DB 업데이트 실패")
                    failed += 1
                
                # Rate limiting
                if idx % 10 == 0:
                    print(f"\n   진행: {idx}/{total} (성공:{success}, 실패:{failed})\n")
                
                time.sleep(1)
            
            except Exception as e:
                print(f"   ❌ 처리 오류: {e}")
                failed += 1
                continue
        
        print(f"\n{'='*60}")
        print(f"✅ OCR 처리 완료!")
        print(f"{'='*60}")
        print(f"   총: {total}개")
        print(f"   성공: {success}개")
        print(f"   실패: {failed}개")
        print(f"{'='*60}\n")
        
        return {'success': success, 'failed': failed}

def main():
    processor = RecentImageOCR()
    processor.process_all()

if __name__ == "__main__":
    main()
