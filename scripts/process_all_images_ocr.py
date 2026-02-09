"""
전체 이미지 OCR + 번역 + DB 업로드 (OpenAI 버전)
"""
import os
import base64
import requests
import json
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image
import time
from datetime import datetime

load_dotenv()

class FullImageProcessor:
    def __init__(self, openai_key: str, supabase_url: str, supabase_key: str):
        self.openai_key = openai_key
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.model = "gpt-4o-mini"
        
        self.headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        
        print(f"✅ OpenAI API (gpt-4o-mini) 로드")
    
    def encode_image(self, image_path: str) -> str:
        """이미지를 base64로 인코딩"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def extract_text_with_openai(self, image_path: str, max_retries: int = 3) -> dict:
        """OpenAI Vision으로 텍스트 추출"""
        for attempt in range(max_retries):
            try:
                # 이미지 정보
                img = Image.open(image_path)
                width, height = img.size
                
                # Base64 인코딩
                base64_image = self.encode_image(image_path)
                
                # OpenAI API 호출
                url = "https://api.openai.com/v1/chat/completions"
                
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.openai_key}"
                }
                
                payload = {
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Perform OCR on this image. Extract all text in original language (Korean/English). Output text only."
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    "max_tokens": 1024,
                    "temperature": 0.1
                }
                
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                
                if response.status_code == 429:
                    wait_time = (attempt + 1) * 5
                    print(f"   ⏳ Rate limit - {wait_time}초 대기 ({attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                
                if response.status_code != 200:
                    if attempt < max_retries - 1:
                        time.sleep(3)
                        continue
                    return {'success': False, 'error': f"API 오류: {response.status_code}"}
                
                result = response.json()
                
                if 'choices' in result and len(result['choices']) > 0:
                    text = result['choices'][0]['message']['content'].strip()
                    
                    return {
                        'success': True,
                        'text': text,
                        'width': width,
                        'height': height
                    }
                else:
                    return {'success': False, 'error': '텍스트 없음'}
            
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(3)
                    continue
                return {'success': False, 'error': str(e)}
        
        return {'success': False, 'error': '최대 재시도 초과'}
    
    def translate_to_korean(self, text: str) -> str:
        """영어 텍스트를 한국어로 번역"""
        try:
            # 한글 비율 확인
            korean_chars = sum(1 for c in text if '\uac00' <= c <= '\ud7a3')
            total_chars = len(text.replace(' ', '').replace('\n', ''))
            
            if total_chars == 0:
                return text
            
            korean_ratio = korean_chars / total_chars
            
            # 50% 이상 한글이면 번역 안 함
            if korean_ratio > 0.5:
                return text
            
            # OpenAI로 번역
            url = "https://api.openai.com/v1/chat/completions"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.openai_key}"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "당신은 전문 번역가입니다. 영어를 한국어로 자연스럽게 번역하세요."},
                    {"role": "user", "content": f"다음 텍스트를 한국어로 번역하세요:\n\n{text}"}
                ],
                "max_tokens": 1024,
                "temperature": 0.3
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=20)
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    translated = result['choices'][0]['message']['content'].strip()
                    return translated
            
            return text
        
        except Exception as e:
            return text
    
    def upload_to_supabase(self, data: dict) -> bool:
        """Supabase DB에 업로드"""
        try:
            url = f"{self.supabase_url}/rest/v1/phishing_images"
            
            response = requests.post(url, headers=self.headers, json=data, timeout=10)
            
            if response.status_code in [201, 200]:
                return True
            elif response.status_code == 409:
                # 중복 - 업데이트 시도
                update_url = f"{url}?image_url=eq.{data['image_url']}"
                update_response = requests.patch(update_url, headers=self.headers, json=data, timeout=10)
                return update_response.status_code in [200, 204]
            else:
                return False
        
        except Exception as e:
            return False
    
    def process_all_images(self, image_dir: str = 'data/images/phishing', skip_count: int = 0):
        """전체 이미지 처리"""
        
        # 이미지 파일 리스트
        image_path = Path(image_dir)
        if not image_path.exists():
            print(f"❌ 이미지 디렉토리가 없습니다: {image_dir}")
            return
        
        image_files = list(image_path.glob('*.jpg')) + list(image_path.glob('*.png'))
        
        if len(image_files) == 0:
            print(f"✅ 처리할 이미지가 없습니다.")
            return
        
        print(f"\n{'='*70}")
        print(f"🚀 이미지 OCR + 번역 + DB 업로드 (OpenAI)")
        print(f"   총 이미지: {len(image_files)}개")
        print(f"   모델: {self.model}")
        print(f"{'='*70}\n")
        
        stats = {
            'total': len(image_files),
            'ocr_success': 0,
            'ocr_failed': 0,
            'translated': 0,
            'uploaded': 0,
            'upload_failed': 0
        }
        
        for idx, image_file in enumerate(image_files, 1):
            print(f"[{idx}/{len(image_files)}] 📸 {image_file.name}")
            
            # 1. OCR
            ocr_result = self.extract_text_with_openai(str(image_file))
            
            if not ocr_result['success']:
                print(f"   ❌ OCR 실패: {ocr_result.get('error', 'Unknown')}")
                stats['ocr_failed'] += 1
                time.sleep(1)
                continue
            
            stats['ocr_success'] += 1
            extracted_text = ocr_result['text']
            
            print(f"   ✅ OCR 성공: {len(extracted_text)}자")
            
            # 2. 번역 (필요시)
            translated_text = self.translate_to_korean(extracted_text)
            
            if translated_text != extracted_text:
                print(f"   🌐 번역 완료")
                stats['translated'] += 1
            
            # 3. DB 업로드 준비
            original_url = f"https://phishing-images/{image_file.name}"
            
            # 언어 감지
            korean_chars = sum(1 for c in translated_text if '\uac00' <= c <= '\ud7a3')
            total_chars = len(translated_text.replace(' ', '').replace('\n', ''))
            language = 'ko' if total_chars > 0 and korean_chars / total_chars > 0.3 else 'en'
            
            upload_data = {
                'image_url': original_url,
                'local_path': str(image_file),
                'query': 'phishing',
                'ocr_text': extracted_text[:5000],
                'translated_text': translated_text[:5000] if translated_text != extracted_text else None,
                'language': language,
                'text_length': len(extracted_text),
                'crawled_at': datetime.now().isoformat(),
                'processed_at': datetime.now().isoformat()
            }
            
            # 4. DB 업로드
            if self.upload_to_supabase(upload_data):
                print(f"   💾 DB 업로드 완료")
                stats['uploaded'] += 1
            else:
                print(f"   ⚠️  DB 업로드 실패")
                stats['upload_failed'] += 1
            
            print()
            time.sleep(1)  # Rate limiting
        
        # 최종 결과
        print(f"\n{'='*70}")
        print(f"✅ 전체 처리 완료!")
        print(f"{'='*70}")
        print(f"   총 이미지: {stats['total']}개")
        print(f"   OCR 성공: {stats['ocr_success']}개")
        print(f"   번역: {stats['translated']}개")
        print(f"   DB 업로드: {stats['uploaded']}개")
        print(f"{'='*70}\n")
        
        return stats

def main():
    openai_key = os.getenv('OPENAI_API_KEY')
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not openai_key:
        print("❌ OPENAI_API_KEY가 없습니다!")
        return
    
    if not all([supabase_url, supabase_key]):
        print("❌ Supabase 환경 변수가 설정되지 않았습니다!")
        return
    
    processor = FullImageProcessor(
        openai_key=openai_key,
        supabase_url=supabase_url,
        supabase_key=supabase_key
    )
    
    processor.process_all_images()

if __name__ == "__main__":
    main()
