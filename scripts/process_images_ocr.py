"""
이미지 OCR + 번역 스크립트
- EasyOCR로 이미지에서 텍스트 추출
- Gemini로 영어 텍스트 번역
"""
import os
import json
import requests
from datetime import datetime
from typing import List, Dict
import easyocr
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

class ImageOCRTranslator:
    def __init__(self):
        print("⏳ EasyOCR 초기화 중... (최초 실행 시 모델 다운로드)")
        self.reader = easyocr.Reader(['ko', 'en'], gpu=False)
        print("✅ EasyOCR 초기화 완료!")
        
    def extract_text_from_image(self, image_path: str) -> Dict:
        """이미지에서 텍스트 추출"""
        try:
            result = self.reader.readtext(image_path)
            
            # 텍스트만 추출
            texts = [item[1] for item in result]
            full_text = ' '.join(texts)
            
            # 언어 감지 (간단한 방법: 영어 비율)
            english_chars = sum(1 for c in full_text if 'a' <= c.lower() <= 'z')
            total_chars = len([c for c in full_text if c.strip()])
            
            is_english = (english_chars / total_chars > 0.5) if total_chars > 0 else False
            
            return {
                'image_path': image_path,
                'raw_text': full_text,
                'is_english': is_english,
                'text_length': len(full_text),
                'extracted_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"   ❌ OCR 실패 ({image_path}): {e}")
            return None
    
    def translate_text(self, text: str) -> str:
        """Gemini로 영어 텍스트 번역"""
        if not text or len(text) < 10:
            return text
        
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
            
            prompt = f"""다음 영어 텍스트를 한국어로 자연스럽게 번역해주세요. 피싱/스캠 관련 용어는 정확하게 번역하세요:

{text}

번역:"""
            
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            }
            
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            result_data = response.json()
            translated = result_data['candidates'][0]['content']['parts'][0]['text'].strip()
            
            return translated
            
        except Exception as e:
            print(f"   ⚠️ 번역 실패: {e}")
            return text
    
    def process_images(self, input_json: str, output_json: str, filter_english_only: bool = True):
        """이미지 메타데이터 JSON에서 이미지 처리"""
        print("="*60)
        print("🖼️  이미지 OCR + 번역 시작")
        print("="*60)
        
        # JSON 로드
        with open(input_json, 'r', encoding='utf-8') as f:
            images_data = json.load(f)
        
        print(f"\n📊 총 이미지: {len(images_data)}개")
        
        results = []
        english_count = 0
        translated_count = 0
        
        for idx, img_data in enumerate(images_data, 1):
            image_path = img_data.get('local_path', '')
            
            if not os.path.exists(image_path):
                print(f"[{idx}/{len(images_data)}] ⚠️  파일 없음: {image_path}")
                continue
            
            print(f"[{idx}/{len(images_data)}] OCR 중...", end=' ')
            
            ocr_result = self.extract_text_from_image(image_path)
            
            if not ocr_result:
                continue
            
            print(f"✅ ({ocr_result['text_length']}자)", end='')
            
            # 영어 텍스트인 경우 번역
            if ocr_result['is_english']:
                english_count += 1
                print(f" 🌐 영어 감지, 번역 중...", end='')
                
                translated_text = self.translate_text(ocr_result['raw_text'])
                ocr_result['translated_text'] = translated_text
                ocr_result['language'] = 'en'
                translated_count += 1
                print(f" ✅ 번역 완료")
            else:
                ocr_result['translated_text'] = ocr_result['raw_text']
                ocr_result['language'] = 'ko'
                print(f" 🇰🇷 한국어")
            
            # 원본 이미지 메타데이터와 병합
            result = {**img_data, **ocr_result}
            results.append(result)
        
        # 저장
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print("\n" + "="*60)
        print("✅ 이미지 OCR + 번역 완료!")
        print(f"   총 처리: {len(results)}개")
        print(f"   영어 감지: {english_count}개")
        print(f"   번역 완료: {translated_count}개")
        print(f"   저장 위치: {output_json}")
        print("="*60)
        
        return results

def main():
    translator = ImageOCRTranslator()
    
    # 입력: 구글 이미지 메타데이터
    input_json = 'data/raw/google_images_20260131_145232.json'
    output_json = 'data/processed/google_images_ocr_translated.json'
    
    os.makedirs('data/processed', exist_ok=True)
    
    translator.process_images(input_json, output_json)

if __name__ == "__main__":
    main()
