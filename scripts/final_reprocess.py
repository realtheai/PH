#!/usr/bin/env python3
"""
실패한 400개 이미지 최종 재처리 (8개 Gemini 키)
"""
import os
import sys
sys.path.append('scripts')

from process_images_dual_ocr import DualOCRProcessor
from dotenv import load_dotenv
import requests
from pathlib import Path
import time
from datetime import datetime

load_dotenv()

openai_key = os.getenv('OPENAI_API_KEY')
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_ANON_KEY')

# Gemini 키 8개
gemini_keys = [
    os.getenv('GEMINI_API_KEY'),
    os.getenv('GEMINI_API_KEY_2'),
    os.getenv('GEMINI_API_KEY_3'),
    os.getenv('GEMINI_API_KEY_4'),
    os.getenv('GEMINI_API_KEY_5'),
    os.getenv('GEMINI_API_KEY_6'),
    os.getenv('GEMINI_API_KEY_7'),
    os.getenv('GEMINI_API_KEY_8'),
]
gemini_keys = [k for k in gemini_keys if k]

print(f"\n🔑 Gemini API 키: {len(gemini_keys)}개 로드됨")

if not all([openai_key, supabase_url, supabase_key]) or not gemini_keys:
    print("❌ 환경 변수가 설정되지 않았습니다!")
    exit(1)

# DB에서 ocr_text가 없는 이미지 찾기
headers = {
    "apikey": supabase_key,
    "Authorization": f"Bearer {supabase_key}",
    "Content-Type": "application/json",
}

print("\n" + "="*100)
print("🔍 실패한 이미지 확인 중...")
print("="*100)

# ocr_text가 null인 레코드 조회 (전체)
response = requests.get(
    f"{supabase_url}/rest/v1/phishing_images?select=local_path,image_url&ocr_text=is.null&limit=1000",
    headers=headers,
    timeout=30
)

if response.status_code == 200:
    failed_records = response.json()
    print(f"\n✅ DB에서 실패 레코드 {len(failed_records)}개 발견")
else:
    print(f"\n⚠️ DB 조회 실패 ({response.status_code})")
    failed_records = []

if not failed_records:
    print("\n✅ 재처리할 이미지가 없습니다!")
    exit(0)

# 로컬 파일 목록 가져오기
image_dir = Path('data/images/phishing')
all_images = {img.name: str(img) for img in list(image_dir.glob('*.jpg')) + list(image_dir.glob('*.png'))}

# 처리할 이미지 목록 생성
failed_images = []
for record in failed_records:
    local_path = record.get('local_path', '')
    image_name = Path(local_path).name if local_path else None
    
    if image_name and image_name in all_images:
        failed_images.append(all_images[image_name])

print(f"📋 재처리 대상: {len(failed_images)}개 이미지")

print("\n" + "="*100)
print(f"🔄 최종 재처리 시작 ({len(failed_images)}개, Gemini 키 {len(gemini_keys)}개)")
print("="*100 + "\n")

# Processor 초기화
processor = DualOCRProcessor(
    openai_key=openai_key,
    gemini_keys=gemini_keys,
    supabase_url=supabase_url,
    supabase_key=supabase_key
)

# 통계
stats = {
    'total': len(failed_images),
    'openai_success': 0,
    'gemini_success': 0,
    'failed': 0,
    'translated': 0,
    'uploaded': 0
}

for idx, image_path in enumerate(failed_images, 1):
    image_file = Path(image_path)
    print(f"[{idx}/{len(failed_images)}] 📸 {image_file.name}")
    
    # OCR
    ocr_result = processor.extract_text(str(image_file))
    
    if not ocr_result['success']:
        print(f"   ❌ OCR 실패: {ocr_result.get('error')}")
        stats['failed'] += 1
        time.sleep(2)  # 실패 시 더 긴 대기
        continue
    
    extracted_text = ocr_result['text']
    model_used = ocr_result['model']
    
    print(f"   ✅ OCR 성공 ({model_used}): {len(extracted_text)}자")
    
    if model_used == 'openai':
        stats['openai_success'] += 1
    else:
        stats['gemini_success'] += 1
    
    # 번역
    translated_text = processor.translate_to_korean(extracted_text)
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
    
    if processor.upload_to_supabase(upload_data):
        print(f"   💾 DB 업로드 완료")
        stats['uploaded'] += 1
    else:
        print(f"   ⚠️  DB 업로드 실패")
    
    print()
    time.sleep(2)  # Gemini rate limit 대비

# 결과
print("\n" + "="*100)
print("✅ 최종 재처리 완료!")
print("="*100)
print(f"   총 이미지: {stats['total']}개")
print(f"   OpenAI 성공: {stats['openai_success']}개")
print(f"   Gemini 성공: {stats['gemini_success']}개")
print(f"   실패: {stats['failed']}개")
print(f"   번역: {stats['translated']}개")
print(f"   DB 업로드: {stats['uploaded']}개")
print(f"   성공률: {(stats['openai_success'] + stats['gemini_success']) / stats['total'] * 100:.1f}%")
print("="*100 + "\n")
