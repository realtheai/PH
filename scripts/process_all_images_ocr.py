"""
전체 이미지 OCR + 번역 + DB 업로드
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
    def __init__(self, api_keys: list, supabase_url: str, supabase_key: str):
        self.gemini_api_keys = api_keys
        self.current_key_index = 0
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.model = "gemini-2.5-flash"
        
        self.headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        
        print(f"✅ API 키 {len(self.gemini_api_keys)}개 로드 (로드 밸런싱 활성화)")
    
    def get_next_api_key(self) -> str:
        """라운드 로빈 방식으로 API 키 순환"""
        key = self.gemini_api_keys[self.current_key_index]
        self.current_key_index = (self.current_key_index + 1) % len(self.gemini_api_keys)
        return key
    
    def encode_image(self, image_path: str) -> str:
        """이미지를 base64로 인코딩"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def extract_text_with_gemini(self, image_path: str, max_retries: int = 3) -> dict:
        """Gemini Vision으로 텍스트 추출 (재시도 포함)"""
        for attempt in range(max_retries):
            try:
                # 이미지 정보
                img = Image.open(image_path)
                width, height = img.size
                
                # Base64 인코딩
                base64_image = self.encode_image(image_path)
                
                # API 키 선택 (로드 밸런싱)
                api_key = self.get_next_api_key()
                
                # Gemini API 호출
                url = f"https://generativelanguage.googleapis.com/v1/models/{self.model}:generateContent?key={api_key}"
                
                prompt = """이 이미지에서 보이는 모든 텍스트를 정확하게 추출해주세요.

출력 형식:
- 한글과 영어를 모두 정확히 추출
- 줄바꿈 유지
- 특수문자 포함
- 광고/배너 제외

텍스트:"""
                
                payload = {
                    "contents": [{
                        "parts": [
                            {"text": prompt},
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
                        "maxOutputTokens": 2048
                    }
                }
                
                response = requests.post(url, json=payload, timeout=30)
                
                if response.status_code == 429:
                    # Rate limit - 재시도
                    wait_time = (attempt + 1) * 10
                    print(f"   ⏳ Rate limit - {wait_time}초 대기 후 재시도 ({attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                
                if response.status_code != 200:
                    if attempt < max_retries - 1:
                        time.sleep(5)
                        continue
                    return {'success': False, 'error': f"API 오류: {response.status_code}"}
                
                result = response.json()
                
                if 'candidates' in result and len(result['candidates']) > 0:
                    text = result['candidates'][0]['content']['parts'][0]['text'].strip()
                    
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
                    time.sleep(5)
                    continue
                return {'success': False, 'error': str(e)}
        
        return {'success': False, 'error': '최대 재시도 초과'}
    
    def translate_to_korean(self, text: str) -> str:
        """영어 텍스트를 한국어로 번역 (필요시)"""
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
            
            # API 키 선택
            api_key = self.get_next_api_key()
            
            # Gemini로 번역
            url = f"https://generativelanguage.googleapis.com/v1/models/{self.model}:generateContent?key={api_key}"
            
            prompt = f"""다음 텍스트를 한국어로 자연스럽게 번역해주세요. 
만약 이미 한국어라면 그대로 출력하세요.

텍스트:
{text}

번역:"""
            
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 2048
                }
            }
            
            response = requests.post(url, json=payload, timeout=20)
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    translated = result['candidates'][0]['content']['parts'][0]['text'].strip()
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
    
    def process_all_images(self, image_dir: str, metadata_file: str = None, skip_count: int = 0):
        """전체 이미지 처리"""
        
        # 메타데이터 로드 (있으면)
        metadata = {}
        if metadata_file and os.path.exists(metadata_file):
            with open(metadata_file, 'r', encoding='utf-8') as f:
                meta_list = json.load(f)
                for item in meta_list:
                    metadata[item['filename']] = item
        
        # 이미지 파일 리스트
        image_path = Path(image_dir)
        image_files = list(image_path.glob('*.jpg')) + list(image_path.glob('*.png'))
        
        # skip_count부터 시작
        if skip_count > 0:
            image_files = image_files[skip_count:]
            print(f"\n⏭️  처음 {skip_count}개 건너뛰기 (이미 처리됨)")
        
        print(f"\n{'='*70}")
        print(f"🚀 전체 이미지 OCR + 번역 + DB 업로드")
        print(f"   총 이미지: {len(image_files)}개 (전체 중 {skip_count}~{skip_count + len(image_files)})")
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
        
        for idx, image_file in enumerate(image_files, skip_count + 1):
            print(f"[{idx}/{skip_count + len(image_files)}] 📸 {image_file.name}")
            
            # 1. OCR
            ocr_result = self.extract_text_with_gemini(str(image_file))
            
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
            # 메타데이터에서 원본 URL 찾기
            original_url = metadata.get(image_file.name, {}).get('image_url')
            
            # URL이 없으면 파일명 기반으로 생성
            if not original_url:
                original_url = f"https://phishing-images/{image_file.name}"
            
            query = metadata.get(image_file.name, {}).get('query', 'phishing')
            
            # 언어 감지
            korean_chars = sum(1 for c in translated_text if '\uac00' <= c <= '\ud7a3')
            total_chars = len(translated_text.replace(' ', '').replace('\n', ''))
            language = 'ko' if total_chars > 0 and korean_chars / total_chars > 0.3 else 'en'
            
            upload_data = {
                'image_url': original_url,
                'local_path': str(image_file),
                'query': query,
                'ocr_text': extracted_text[:5000],  # 길이 제한
                'translated_text': translated_text[:5000] if translated_text != extracted_text else None,  # 번역본만
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
            
            # Rate limiting (3개 키로 분당 45회 가능)
            # 안전하게 2초 대기 (시간당 1800개, 571개는 약 20분 소요)
            time.sleep(2)
            
            # 진행 상황 출력 (매 50개마다)
            if (idx - skip_count) % 50 == 0:
                print(f"\n{'='*70}")
                print(f"📊 중간 통계 ({idx}/{skip_count + len(image_files)})")
                print(f"   OCR 성공: {stats['ocr_success']}개")
                print(f"   번역: {stats['translated']}개")
                print(f"   DB 업로드: {stats['uploaded']}개")
                print(f"{'='*70}\n")
        
        # 최종 결과
        print(f"\n{'='*70}")
        print(f"✅ 전체 처리 완료!")
        print(f"{'='*70}")
        print(f"   총 이미지: {stats['total']}개")
        print(f"   OCR 성공: {stats['ocr_success']}개 ({stats['ocr_success']/stats['total']*100:.1f}%)")
        print(f"   OCR 실패: {stats['ocr_failed']}개")
        print(f"   번역 처리: {stats['translated']}개")
        print(f"   DB 업로드: {stats['uploaded']}개 ({stats['uploaded']/stats['total']*100:.1f}%)")
        print(f"   업로드 실패: {stats['upload_failed']}개")
        print(f"{'='*70}\n")
        
        return stats

def main():
    # 환경 변수 로드
    load_dotenv()
    
    # 모든 Gemini API 키 수집
    api_keys = []
    for i in range(1, 10):  # 최대 9개까지 지원
        if i == 1:
            key = os.getenv('GEMINI_API_KEY')
        else:
            key = os.getenv(f'GEMINI_API_KEY_{i}')
        
        if key:
            api_keys.append(key)
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not api_keys:
        print("❌ 사용 가능한 GEMINI_API_KEY가 없습니다!")
        return
    
    if not all([supabase_url, supabase_key]):
        print("❌ Supabase 환경 변수가 설정되지 않았습니다!")
        return
    
    processor = FullImageProcessor(
        api_keys=api_keys,
        supabase_url=supabase_url,
        supabase_key=supabase_key
    )
    
    # 이미지 처리 (542번부터 재개 - 나머지 29개)
    processor.process_all_images(
        image_dir='data/images/phishing',
        metadata_file='data/raw/google_images_20260131_145232.json',
        skip_count=542
    )

if __name__ == "__main__":
    main()
