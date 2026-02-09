#!/usr/bin/env python3
"""
개선된 OCR 프롬프트 테스트 (5개 샘플)
"""
import os
import sys
sys.path.append('scripts')

from process_all_images_ocr import FullImageProcessor
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

openai_key = os.getenv('OPENAI_API_KEY')
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_ANON_KEY')

if not all([openai_key, supabase_url, supabase_key]):
    print("❌ 환경 변수가 설정되지 않았습니다!")
    exit(1)

processor = FullImageProcessor(
    openai_key=openai_key,
    supabase_url=supabase_url,
    supabase_key=supabase_key
)

# 테스트 이미지 (기존에 문제 있었던 이미지들)
test_images = [
    "data/images/phishing/스미싱_문자_사례_2.jpg",
    "data/images/phishing/스미싱_문자_사례_3.jpg",
    "data/images/phishing/스미싱_문자_사례_4.jpg",
    "data/images/phishing/결제_알림_피싱_문자_17.jpg",
    "data/images/phishing/스미싱_문자_사례_9.jpg",
]

print("\n" + "="*100)
print("🧪 개선된 OCR 프롬프트 테스트")
print("="*100 + "\n")

success_count = 0
failed_count = 0

for idx, img_path in enumerate(test_images, 1):
    if not os.path.exists(img_path):
        print(f"[{idx}/{len(test_images)}] ⚠️ 파일 없음: {img_path}\n")
        continue
    
    print(f"[{idx}/{len(test_images)}] 📸 {os.path.basename(img_path)}")
    
    result = processor.extract_text_with_openai(img_path)
    
    if result['success']:
        text = result['text']
        
        # 거부 체크
        if "추출할 수 없습니다" in text or "cannot" in text.lower() or "can't" in text.lower() or "unable" in text.lower():
            print(f"   ❌ OpenAI 거부: {text[:80]}...")
            failed_count += 1
        else:
            print(f"   ✅ 성공: {len(text)}자 추출")
            print(f"   📝 텍스트: {text[:100]}...")
            success_count += 1
    else:
        print(f"   ❌ 실패: {result.get('error', 'Unknown')}")
        failed_count += 1
    
    print()

print("="*100)
print(f"📊 결과: ✅ 성공 {success_count}개 / ❌ 실패 {failed_count}개")
print("="*100)
