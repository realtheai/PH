"""
이미지 OCR 처리 (OpenAI + Gemini Fallback)
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

class DualOCRProcessor:
    def __init__(self, openai_key: str, gemini_keys: list, supabase_url: str, supabase_key: str):
        self.openai_key = openai_key
        self.gemini_keys = gemini_keys
        self.current_gemini_idx = 0
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        
        self.headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        
        print(f"✅ Dual OCR Processor 로드")
        print(f"   - OpenAI: gpt-4o-mini")
        print(f"   - Gemini: gemini-2.5-flash (Fallback, {len(gemini_keys)}개 키)")
    
    def encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')
    
    def extract_with_openai(self, image_path: str) -> dict:
        """OpenAI Vision으로 OCR"""
        try:
            base64_image = self.encode_image(image_path)
            
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
                            {"type": "text", "text": "Perform OCR on this image. Extract all text in original language (Korean/English). Output text only."},
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
                
                # 거부 체크
                reject_keywords = ["추출할 수 없습니다", "cannot", "can't", "unable", "sorry"]
                if any(keyword in text.lower() for keyword in reject_keywords):
                    return {'success': False, 'reason': 'rejected', 'text': text}
                
                return {'success': True, 'text': text, 'model': 'openai'}
            else:
                return {'success': False, 'reason': f'status_{response.status_code}'}
        
        except Exception as e:
            return {'success': False, 'reason': str(e)}
    
    def extract_with_gemini(self, image_path: str) -> dict:
        """Gemini Vision으로 OCR"""
        try:
            base64_image = self.encode_image(image_path)
            
            # 현재 키 사용
            gemini_key = self.gemini_keys[self.current_gemini_idx]
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
            
            payload = {
                "contents": [{
                    "parts": [
                        {"text": "Extract all visible text from this image. Output only the actual text content in the original language (Korean or English). Do not include any formatting tags, labels, or descriptions. Just output the text as it appears."},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": base64_image
                            }
                        }
                    ]
                }],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 1024,
                }
            }
            
            response = requests.post(url, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                
                if 'candidates' in result and len(result['candidates']) > 0:
                    text = result['candidates'][0]['content']['parts'][0]['text'].strip()
                    return {'success': True, 'text': text, 'model': 'gemini'}
                else:
                    return {'success': False, 'reason': 'no_candidates'}
            elif response.status_code == 429:
                # Rate limit - 다음 키로 전환
                self.current_gemini_idx = (self.current_gemini_idx + 1) % len(self.gemini_keys)
                return {'success': False, 'reason': 'rate_limit'}
            else:
                return {'success': False, 'reason': f'status_{response.status_code}'}
        
        except Exception as e:
            return {'success': False, 'reason': str(e)}
    
    def extract_text(self, image_path: str) -> dict:
        """OCR 추출 (OpenAI 우선, 실패 시 Gemini)"""
        # 이미지 정보
        img = Image.open(image_path)
        width, height = img.size
        
        # 1. OpenAI 시도
        openai_result = self.extract_with_openai(image_path)
        
        if openai_result['success']:
            return {
                'success': True,
                'text': openai_result['text'],
                'model': 'openai',
                'width': width,
                'height': height
            }
        
        # 2. OpenAI 실패 -> Gemini Fallback
        print(f"   🔄 OpenAI 실패 ({openai_result.get('reason')}), Gemini로 재시도...")
        
        gemini_result = self.extract_with_gemini(image_path)
        
        if gemini_result['success']:
            return {
                'success': True,
                'text': gemini_result['text'],
                'model': 'gemini',
                'width': width,
                'height': height
            }
        
        # 3. 둘 다 실패
        return {
            'success': False,
            'error': f"OpenAI: {openai_result.get('reason')}, Gemini: {gemini_result.get('reason')}"
        }
    
    def translate_to_korean(self, text: str) -> str:
        """영어 텍스트를 한국어로 번역"""
        try:
            korean_chars = sum(1 for c in text if '\uac00' <= c <= '\ud7a3')
            total_chars = len(text.replace(' ', '').replace('\n', ''))
            
            if total_chars == 0 or korean_chars / total_chars > 0.5:
                return text
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.openai_key}"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "당신은 전문 번역가입니다. 영어를 한국어로 자연스럽게 번역하세요."},
                        {"role": "user", "content": f"다음 텍스트를 한국어로 번역하세요:\n\n{text}"}
                    ],
                    "max_tokens": 1024,
                    "temperature": 0.3
                },
                timeout=20
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content'].strip()
            
            return text
        
        except Exception:
            return text
    
    def upload_to_supabase(self, data: dict) -> bool:
        """Supabase DB에 업로드"""
        try:
            url = f"{self.supabase_url}/rest/v1/phishing_images"
            
            response = requests.post(url, headers=self.headers, json=data, timeout=10)
            
            if response.status_code in [201, 200]:
                return True
            elif response.status_code == 409:
                update_url = f"{url}?image_url=eq.{data['image_url']}"
                update_response = requests.patch(update_url, headers=self.headers, json=data, timeout=10)
                return update_response.status_code in [200, 204]
            else:
                return False
        
        except Exception:
            return False
    
    def process_all_images(self, image_dir: str = 'data/images/phishing'):
        """전체 이미지 처리"""
        image_path = Path(image_dir)
        if not image_path.exists():
            print(f"❌ 이미지 디렉토리가 없습니다: {image_dir}")
            return
        
        image_files = list(image_path.glob('*.jpg')) + list(image_path.glob('*.png'))
        
        print(f"\n{'='*100}")
        print(f"🚀 Dual OCR 처리 시작")
        print(f"   총 이미지: {len(image_files)}개")
        print(f"{'='*100}\n")
        
        stats = {
            'total': len(image_files),
            'openai_success': 0,
            'gemini_success': 0,
            'failed': 0,
            'translated': 0,
            'uploaded': 0
        }
        
        for idx, image_file in enumerate(image_files, 1):
            print(f"[{idx}/{len(image_files)}] 📸 {image_file.name}")
            
            # OCR
            ocr_result = self.extract_text(str(image_file))
            
            if not ocr_result['success']:
                print(f"   ❌ OCR 실패: {ocr_result.get('error')}")
                stats['failed'] += 1
                time.sleep(1)
                continue
            
            extracted_text = ocr_result['text']
            model_used = ocr_result['model']
            
            print(f"   ✅ OCR 성공 ({model_used}): {len(extracted_text)}자")
            
            if model_used == 'openai':
                stats['openai_success'] += 1
            else:
                stats['gemini_success'] += 1
            
            # 번역
            translated_text = self.translate_to_korean(extracted_text)
            if translated_text != extracted_text:
                print(f"   🌐 번역 완료")
                stats['translated'] += 1
            
            # DB 업로드
            original_url = f"https://phishing-images/{image_file.name}"
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
            
            if self.upload_to_supabase(upload_data):
                print(f"   💾 DB 업로드 완료")
                stats['uploaded'] += 1
            else:
                print(f"   ⚠️  DB 업로드 실패")
            
            print()
            time.sleep(1.5)
        
        # 결과
        print(f"\n{'='*100}")
        print(f"✅ 전체 처리 완료!")
        print(f"{'='*100}")
        print(f"   총 이미지: {stats['total']}개")
        print(f"   OpenAI 성공: {stats['openai_success']}개")
        print(f"   Gemini 성공: {stats['gemini_success']}개")
        print(f"   실패: {stats['failed']}개")
        print(f"   번역: {stats['translated']}개")
        print(f"   DB 업로드: {stats['uploaded']}개")
        print(f"{'='*100}\n")
        
        return stats

def main():
    openai_key = os.getenv('OPENAI_API_KEY')
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    # Gemini 키 로드 (6개)
    gemini_keys = [
        os.getenv('GEMINI_API_KEY'),
        os.getenv('GEMINI_API_KEY_2'),
        os.getenv('GEMINI_API_KEY_3'),
        os.getenv('GEMINI_API_KEY_4'),
        os.getenv('GEMINI_API_KEY_5'),
        os.getenv('GEMINI_API_KEY_6'),
    ]
    gemini_keys = [k for k in gemini_keys if k]  # None 제거
    
    if not all([openai_key, supabase_url, supabase_key]) or not gemini_keys:
        print("❌ 환경 변수가 설정되지 않았습니다!")
        return
    
    processor = DualOCRProcessor(
        openai_key=openai_key,
        gemini_keys=gemini_keys,
        supabase_url=supabase_url,
        supabase_key=supabase_key
    )
    
    processor.process_all_images()

if __name__ == "__main__":
    main()
