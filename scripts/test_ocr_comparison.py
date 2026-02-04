"""
OCR 성능 테스트: EasyOCR vs Gemini Vision
"""
import os
import time
import random
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

def test_easyocr(image_path: str):
    """EasyOCR 테스트"""
    try:
        import easyocr
        
        print(f"\n📷 테스트 이미지: {os.path.basename(image_path)}")
        print("-" * 60)
        
        # EasyOCR 리더 생성 (한국어 + 영어)
        print("⏳ EasyOCR 초기화 중...")
        start = time.time()
        reader = easyocr.Reader(['ko', 'en'], gpu=False)
        init_time = time.time() - start
        print(f"   초기화 시간: {init_time:.2f}초")
        
        # OCR 실행
        print("⏳ OCR 실행 중...")
        start = time.time()
        result = reader.readtext(image_path)
        ocr_time = time.time() - start
        
        print(f"   OCR 시간: {ocr_time:.2f}초")
        print(f"   감지된 텍스트 블록: {len(result)}개")
        
        # 결과 출력
        if result:
            print("\n📝 추출된 텍스트:")
            full_text = []
            for detection in result:
                text = detection[1]
                confidence = detection[2]
                full_text.append(text)
                print(f"   [{confidence:.2f}] {text}")
            
            combined = ' '.join(full_text)
            print(f"\n📄 전체 텍스트:\n   {combined}")
            return combined, ocr_time
        else:
            print("   ❌ 텍스트 감지 실패")
            return "", ocr_time
            
    except Exception as e:
        print(f"   ❌ EasyOCR 오류: {e}")
        return None, 0

def test_gemini_vision(image_path: str):
    """Gemini Vision API 테스트"""
    try:
        import base64
        import requests
        
        print(f"\n🤖 Gemini Vision 테스트")
        print("-" * 60)
        
        # 이미지를 base64로 인코딩
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Gemini API 호출
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [
                    {"text": "이 이미지에서 모든 텍스트를 추출해주세요. 한글과 영어 모두 포함해주세요. 텍스트만 반환하고 설명은 하지 마세요."},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": image_data
                        }
                    }
                ]
            }]
        }
        
        print("⏳ Gemini Vision 실행 중...")
        start = time.time()
        response = requests.post(url, json=payload, timeout=30)
        ocr_time = time.time() - start
        
        if response.status_code == 200:
            result = response.json()
            text = result['candidates'][0]['content']['parts'][0]['text']
            
            print(f"   OCR 시간: {ocr_time:.2f}초")
            print(f"\n📝 추출된 텍스트:\n   {text}")
            return text, ocr_time
        else:
            print(f"   ❌ API 오류: {response.status_code}")
            print(f"   {response.text[:200]}")
            return None, ocr_time
            
    except Exception as e:
        print(f"   ❌ Gemini Vision 오류: {e}")
        return None, 0

def main():
    print("="*60)
    print("🔬 OCR 성능 비교 테스트")
    print("="*60)
    
    # 테스트할 이미지 선택 (랜덤 3개)
    image_dir = Path('data/images/phishing')
    images = list(image_dir.glob('*.jpg'))
    
    if not images:
        print("❌ 이미지 파일이 없습니다.")
        return
    
    # 다양한 유형 선택
    test_images = random.sample(images, min(3, len(images)))
    
    results = {
        'easyocr': {'times': [], 'success': 0},
        'gemini': {'times': [], 'success': 0}
    }
    
    for idx, img_path in enumerate(test_images, 1):
        print(f"\n{'='*60}")
        print(f"테스트 {idx}/3: {img_path.name}")
        print('='*60)
        
        # EasyOCR 테스트
        easy_text, easy_time = test_easyocr(str(img_path))
        if easy_text is not None:
            results['easyocr']['times'].append(easy_time)
            if easy_text:
                results['easyocr']['success'] += 1
        
        # Gemini Vision 테스트
        gemini_text, gemini_time = test_gemini_vision(str(img_path))
        if gemini_text is not None:
            results['gemini']['times'].append(gemini_time)
            if gemini_text:
                results['gemini']['success'] += 1
        
        print("\n" + "="*60)
    
    # 최종 비교
    print("\n" + "="*60)
    print("📊 최종 비교 결과")
    print("="*60)
    
    if results['easyocr']['times']:
        avg_easy = sum(results['easyocr']['times']) / len(results['easyocr']['times'])
        print(f"\n🟦 EasyOCR:")
        print(f"   평균 시간: {avg_easy:.2f}초")
        print(f"   성공: {results['easyocr']['success']}/{len(test_images)}")
    
    if results['gemini']['times']:
        avg_gemini = sum(results['gemini']['times']) / len(results['gemini']['times'])
        print(f"\n🟩 Gemini Vision:")
        print(f"   평균 시간: {avg_gemini:.2f}초")
        print(f"   성공: {results['gemini']['success']}/{len(test_images)}")
    
    # 추천
    print("\n" + "="*60)
    print("💡 추천")
    print("="*60)
    
    if results['gemini']['success'] > results['easyocr']['success']:
        print("✅ Gemini Vision 추천")
        print("   - 더 정확한 텍스트 추출")
    elif results['easyocr']['success'] > 0:
        print("✅ EasyOCR 추천")
        print("   - 무료")
        print("   - 빠른 속도")
    else:
        print("⚠️  둘 다 테스트 필요")
    
    print("="*60)

if __name__ == "__main__":
    main()
