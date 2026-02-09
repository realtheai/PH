#!/usr/bin/env python3
"""
OpenAI Vision 성공/실패 이미지 특성 분석
"""
import os
import base64
from PIL import Image

def analyze_image(image_path):
    """이미지 특성 분석"""
    try:
        # 파일 크기
        file_size = os.path.getsize(image_path)
        
        # 이미지 정보
        img = Image.open(image_path)
        width, height = img.size
        format_type = img.format
        mode = img.mode
        
        # Base64 크기
        with open(image_path, "rb") as f:
            base64_size = len(base64.b64encode(f.read()).decode('utf-8'))
        
        return {
            'file_size': file_size,
            'file_size_kb': file_size / 1024,
            'width': width,
            'height': height,
            'pixels': width * height,
            'format': format_type,
            'mode': mode,
            'base64_size': base64_size,
            'base64_size_kb': base64_size / 1024
        }
    except Exception as e:
        return {'error': str(e)}

# 테스트 이미지들
test_images = {
    '✅ OpenAI 성공 케이스': [
        'data/images/phishing/결제_알림_피싱_문자_17.jpg',
        'data/images/phishing/스미싱_문자_사례_9.jpg',  # 일부 성공
    ],
    '❌ OpenAI 실패 케이스': [
        'data/images/phishing/스미싱_문자_사례_2.jpg',
        'data/images/phishing/스미싱_문자_사례_3.jpg',
        'data/images/phishing/스미싱_문자_사례_4.jpg',
    ]
}

print("\n" + "="*100)
print("🔍 OpenAI Vision 성공/실패 이미지 특성 분석")
print("="*100 + "\n")

all_stats = {'success': [], 'failed': []}

for category, images in test_images.items():
    print(f"\n{'='*100}")
    print(f"{category}")
    print(f"{'='*100}\n")
    
    for img_path in images:
        if not os.path.exists(img_path):
            print(f"⚠️ 파일 없음: {img_path}\n")
            continue
        
        info = analyze_image(img_path)
        
        if 'error' in info:
            print(f"❌ {os.path.basename(img_path)}: {info['error']}\n")
            continue
        
        print(f"📸 {os.path.basename(img_path)}")
        print(f"   파일 크기: {info['file_size_kb']:.1f} KB")
        print(f"   해상도: {info['width']} × {info['height']} ({info['pixels']:,} pixels)")
        print(f"   형식: {info['format']} ({info['mode']})")
        print(f"   Base64 크기: {info['base64_size_kb']:.1f} KB")
        print()
        
        # 통계 저장
        if '성공' in category:
            all_stats['success'].append(info)
        else:
            all_stats['failed'].append(info)

# 평균 비교
print("\n" + "="*100)
print("📊 평균 비교")
print("="*100 + "\n")

if all_stats['success']:
    success_avg = {
        'file_size_kb': sum(s['file_size_kb'] for s in all_stats['success']) / len(all_stats['success']),
        'width': sum(s['width'] for s in all_stats['success']) / len(all_stats['success']),
        'height': sum(s['height'] for s in all_stats['success']) / len(all_stats['success']),
        'pixels': sum(s['pixels'] for s in all_stats['success']) / len(all_stats['success']),
        'base64_kb': sum(s['base64_size_kb'] for s in all_stats['success']) / len(all_stats['success'])
    }
    
    print(f"✅ 성공 케이스 평균 ({len(all_stats['success'])}개):")
    print(f"   파일 크기: {success_avg['file_size_kb']:.1f} KB")
    print(f"   해상도: {success_avg['width']:.0f} × {success_avg['height']:.0f}")
    print(f"   픽셀 수: {success_avg['pixels']:,.0f}")
    print(f"   Base64 크기: {success_avg['base64_kb']:.1f} KB")
    print()

if all_stats['failed']:
    failed_avg = {
        'file_size_kb': sum(s['file_size_kb'] for s in all_stats['failed']) / len(all_stats['failed']),
        'width': sum(s['width'] for s in all_stats['failed']) / len(all_stats['failed']),
        'height': sum(s['height'] for s in all_stats['failed']) / len(all_stats['failed']),
        'pixels': sum(s['pixels'] for s in all_stats['failed']) / len(all_stats['failed']),
        'base64_kb': sum(s['base64_size_kb'] for s in all_stats['failed']) / len(all_stats['failed'])
    }
    
    print(f"❌ 실패 케이스 평균 ({len(all_stats['failed'])}개):")
    print(f"   파일 크기: {failed_avg['file_size_kb']:.1f} KB")
    print(f"   해상도: {failed_avg['width']:.0f} × {failed_avg['height']:.0f}")
    print(f"   픽셀 수: {failed_avg['pixels']:,.0f}")
    print(f"   Base64 크기: {failed_avg['base64_kb']:.1f} KB")
    print()

# 차이 분석
if all_stats['success'] and all_stats['failed']:
    print("🔍 차이 분석:")
    print(f"   파일 크기 비율: {failed_avg['file_size_kb'] / success_avg['file_size_kb']:.2f}x")
    print(f"   해상도 비율: {failed_avg['pixels'] / success_avg['pixels']:.2f}x")
    print(f"   Base64 비율: {failed_avg['base64_kb'] / success_avg['base64_kb']:.2f}x")

print("\n" + "="*100)
print("✅ 분석 완료!")
print("="*100)
