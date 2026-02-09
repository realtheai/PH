#!/usr/bin/env python3
"""
Dual OCR 전략 테스트 (5개 샘플)
"""
import os
import sys
sys.path.append('scripts')

from process_images_dual_ocr import DualOCRProcessor
from dotenv import load_dotenv

load_dotenv()

openai_key = os.getenv('OPENAI_API_KEY')
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_ANON_KEY')

gemini_keys = [
    os.getenv('GEMINI_API_KEY'),
    os.getenv('GEMINI_API_KEY_2'),
    os.getenv('GEMINI_API_KEY_3'),
    os.getenv('GEMINI_API_KEY_4'),
    os.getenv('GEMINI_API_KEY_5'),
    os.getenv('GEMINI_API_KEY_6'),
]
gemini_keys = [k for k in gemini_keys if k]

if not all([openai_key, supabase_url, supabase_key]) or not gemini_keys:
    print("❌ 환경 변수가 설정되지 않았습니다!")
    exit(1)

processor = DualOCRProcessor(
    openai_key=openai_key,
    gemini_keys=gemini_keys,
    supabase_url=supabase_url,
    supabase_key=supabase_key
)

# 테스트 이미지
test_images = [
    "data/images/phishing/스미싱_문자_사례_2.jpg",
    "data/images/phishing/스미싱_문자_사례_3.jpg",
    "data/images/phishing/스미싱_문자_사례_4.jpg",  # OpenAI 거부
    "data/images/phishing/결제_알림_피싱_문자_17.jpg",
    "data/images/phishing/스미싱_문자_사례_9.jpg",
]

print("\n" + "="*100)
print("🧪 Dual OCR 전략 테스트")
print("="*100 + "\n")

success_count = 0
openai_count = 0
gemini_count = 0
failed_count = 0

for idx, img_path in enumerate(test_images, 1):
    if not os.path.exists(img_path):
        print(f"[{idx}/{len(test_images)}] ⚠️ 파일 없음: {img_path}\n")
        continue
    
    print(f"[{idx}/{len(test_images)}] 📸 {os.path.basename(img_path)}")
    
    result = processor.extract_text(img_path)
    
    if result['success']:
        text = result['text']
        model = result['model']
        
        print(f"   ✅ 성공 ({model}): {len(text)}자 추출")
        print(f"   📝 텍스트: {text[:100]}...")
        success_count += 1
        
        if model == 'openai':
            openai_count += 1
        else:
            gemini_count += 1
    else:
        print(f"   ❌ 실패: {result.get('error', 'Unknown')}")
        failed_count += 1
    
    print()

print("="*100)
print(f"📊 결과:")
print(f"   ✅ 전체 성공: {success_count}/{len(test_images)}")
print(f"   🟦 OpenAI: {openai_count}개")
print(f"   🟩 Gemini: {gemini_count}개")
print(f"   ❌ 실패: {failed_count}개")
print("="*100)
