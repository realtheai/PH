"""
Gemini Vision API를 사용한 이미지 OCR 테스트
"""
import os
import base64
import requests
import json
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image
import time

load_dotenv()

class GeminiVisionOCR:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = "gemini-2.5-flash"  # Vision 지원 모델
        
    def encode_image(self, image_path: str) -> str:
        """이미지를 base64로 인코딩"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def extract_text(self, image_path: str, language: str = "auto") -> dict:
        """Gemini Vision으로 텍스트 추출"""
        try:
            # 이미지 크기 확인
            img = Image.open(image_path)
            width, height = img.size
            
            # Base64 인코딩
            base64_image = self.encode_image(image_path)
            
            # Gemini API 호출
            url = f"https://generativelanguage.googleapis.com/v1/models/{self.model}:generateContent?key={self.api_key}"
            
            headers = {
                "Content-Type": "application/json"
            }
            
            # 프롬프트: 이미지에서 텍스트 추출
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
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f"API 오류: {response.status_code} - {response.text}",
                    'image_size': f"{width}x{height}",
                    'extracted_text': None
                }
            
            result = response.json()
            
            # 응답에서 텍스트 추출
            if 'candidates' in result and len(result['candidates']) > 0:
                text = result['candidates'][0]['content']['parts'][0]['text']
                
                return {
                    'success': True,
                    'image_size': f"{width}x{height}",
                    'extracted_text': text.strip(),
                    'char_count': len(text.strip()),
                    'has_korean': any('\uac00' <= c <= '\ud7a3' for c in text),
                    'has_english': any(c.isalpha() and ord(c) < 128 for c in text)
                }
            else:
                return {
                    'success': False,
                    'error': '텍스트를 찾을 수 없음',
                    'image_size': f"{width}x{height}",
                    'extracted_text': None
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'extracted_text': None
            }

def test_sample_images(num_samples: int = 5):
    """샘플 이미지로 OCR 테스트"""
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY가 .env에 없습니다!")
        return
    
    ocr = GeminiVisionOCR(api_key)
    
    # 이미지 디렉토리
    image_dir = Path('data/images/phishing')
    
    if not image_dir.exists():
        print(f"❌ 이미지 디렉토리가 없습니다: {image_dir}")
        return
    
    # 이미지 파일 리스트
    image_files = list(image_dir.glob('*.jpg')) + list(image_dir.glob('*.png'))
    
    if not image_files:
        print(f"❌ 이미지 파일이 없습니다: {image_dir}")
        return
    
    # 랜덤 샘플 선택
    import random
    random.seed(42)
    sample_images = random.sample(image_files, min(num_samples, len(image_files)))
    
    print(f"\n{'='*70}")
    print(f"🧪 Gemini Vision OCR 테스트")
    print(f"   모델: gemini-2.5-flash")
    print(f"   샘플 수: {len(sample_images)}개")
    print(f"{'='*70}\n")
    
    results = []
    success_count = 0
    total_chars = 0
    
    for idx, image_path in enumerate(sample_images, 1):
        print(f"[{idx}/{len(sample_images)}] 📸 {image_path.name}")
        
        # OCR 실행
        result = ocr.extract_text(str(image_path))
        
        if result['success']:
            success_count += 1
            total_chars += result['char_count']
            
            print(f"   ✅ 성공!")
            print(f"   📏 이미지 크기: {result['image_size']}")
            print(f"   📝 추출된 문자 수: {result['char_count']}자")
            print(f"   🇰🇷 한글 포함: {'예' if result['has_korean'] else '아니오'}")
            print(f"   🇺🇸 영어 포함: {'예' if result['has_english'] else '아니오'}")
            print(f"\n   --- 추출된 텍스트 ---")
            print(f"   {result['extracted_text'][:200]}{'...' if len(result['extracted_text']) > 200 else ''}")
            print()
        else:
            print(f"   ❌ 실패: {result['error']}")
            if 'image_size' in result:
                print(f"   📏 이미지 크기: {result['image_size']}")
            print()
        
        results.append({
            'filename': image_path.name,
            **result
        })
        
        # Rate limiting
        time.sleep(2)
    
    # 결과 요약
    print(f"\n{'='*70}")
    print(f"📊 테스트 결과 요약")
    print(f"{'='*70}")
    print(f"   총 시도: {len(sample_images)}개")
    print(f"   성공: {success_count}개 ({success_count/len(sample_images)*100:.1f}%)")
    print(f"   실패: {len(sample_images) - success_count}개")
    
    if success_count > 0:
        print(f"\n   평균 추출 문자 수: {total_chars // success_count}자")
        
        korean_count = sum(1 for r in results if r.get('has_korean'))
        english_count = sum(1 for r in results if r.get('has_english'))
        
        print(f"   한글 포함: {korean_count}개")
        print(f"   영어 포함: {english_count}개")
    
    print(f"{'='*70}\n")
    
    # 결과 저장
    output_file = 'data/test_gemini_ocr_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"💾 결과 저장: {output_file}\n")
    
    return results

if __name__ == "__main__":
    test_sample_images(num_samples=5)
