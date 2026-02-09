#!/usr/bin/env python3
"""
OpenAI Vision 거부 이미지 내용 확인 (OCR 비교)
"""
import os
import subprocess

images = [
    ("data/images/phishing/결제_알림_피싱_문자_17.jpg", "✅ OpenAI 성공"),
    ("data/images/phishing/스미싱_문자_사례_2.jpg", "❌ OpenAI 거부"),
    ("data/images/phishing/스미싱_문자_사례_3.jpg", "❌ OpenAI 거부"),
]

print("\n" + "="*100)
print("🔍 거부된 이미지 OCR 비교 (Tesseract)")
print("="*100 + "\n")

for img_path, desc in images:
    if not os.path.exists(img_path):
        print(f"⚠️ 파일 없음: {img_path}\n")
        continue
    
    print(f"{'='*100}")
    print(f"{desc}: {os.path.basename(img_path)}")
    print(f"{'='*100}")
    
    try:
        # Tesseract OCR로 텍스트 추출 (한국어+영어)
        result = subprocess.run(
            ['tesseract', img_path, 'stdout', '-l', 'kor+eng'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        text = result.stdout.strip()
        if text:
            print(f"\n추출된 텍스트:\n{text}\n")
        else:
            print("\n(텍스트 없음)\n")
            
    except FileNotFoundError:
        print("⚠️ Tesseract가 설치되지 않았습니다. 이미지 뷰어로 확인하세요.\n")
        break
    except Exception as e:
        print(f"❌ 에러: {e}\n")

print("="*100)
print("✅ 완료")
print("="*100)
