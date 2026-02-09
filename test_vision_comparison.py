#!/usr/bin/env python3
"""
Llama3.2-Vision vs OpenAI Vision OCR 비교 테스트
"""
import os
import requests
import json
import time
import base64
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

OPENAI_KEY = os.getenv('OPENAI_API_KEY')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

db_headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

def encode_image(image_path):
    """이미지를 base64로 인코딩"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def ocr_with_llama_vision(image_path):
    """Llama3.2-Vision으로 OCR"""
    try:
        start = time.time()
        
        # Base64 인코딩
        base64_image = encode_image(image_path)
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2-vision:11b",
                "prompt": "Extract all text from this image. Output only the text, nothing else.",
                "images": [base64_image],
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 500
                }
            },
            timeout=120
        )
        
        elapsed = time.time() - start
        
        if response.status_code == 200:
            result = response.json()
            text = result.get('response', '').strip()
            return {
                'success': True,
                'text': text,
                'time': elapsed,
                'length': len(text)
            }
        else:
            return {
                'success': False,
                'error': f"Status {response.status_code}",
                'time': elapsed
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'time': 0
        }

def ocr_with_openai(image_path):
    """OpenAI Vision으로 OCR"""
    try:
        start = time.time()
        
        # Base64 인코딩
        base64_image = encode_image(image_path)
        
        url = "https://api.openai.com/v1/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_KEY}"
        }
        
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "이 이미지에서 보이는 모든 텍스트를 정확하게 추출해주세요. 한글과 영어를 모두 정확히 추출하고, 줄바꿈을 유지하세요."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 1024,
            "temperature": 0.2
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        elapsed = time.time() - start
        
        if response.status_code == 200:
            result = response.json()
            text = result['choices'][0]['message']['content'].strip()
            return {
                'success': True,
                'text': text,
                'time': elapsed,
                'length': len(text)
            }
        else:
            return {
                'success': False,
                'error': f"Status {response.status_code}",
                'time': elapsed
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'time': 0
        }

def main():
    print("\n" + "="*80)
    print("🔍 Llama3.2-Vision vs OpenAI Vision OCR 비교 테스트")
    print("="*80 + "\n")
    
    # 1. 이미지 10개 가져오기
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/phishing_images",
        headers=db_headers,
        params={
            'select': 'id,local_path,ocr_text',
            'limit': 10
        }
    )
    
    if response.status_code != 200:
        print(f"❌ 이미지 조회 실패: {response.status_code}")
        return
    
    images = response.json()
    
    if not images:
        print("❌ 이미지가 없습니다!")
        return
    
    print(f"📸 테스트 이미지: {len(images)}개\n")
    
    # 통계
    stats = {
        'llama': {'success': 0, 'failed': 0, 'total_time': 0, 'total_length': 0},
        'openai': {'success': 0, 'failed': 0, 'total_time': 0, 'total_length': 0}
    }
    
    results = []
    
    for i, img in enumerate(images, 1):
        img_id = img['id']
        img_path = img['local_path']
        original_text = img.get('ocr_text', '')
        
        print(f"[{i}/10] ID: {img_id}")
        print(f"   파일: {img_path}")
        if original_text:
            print(f"   기존 OCR: {original_text[:50]}..." if len(original_text) > 50 else f"   기존 OCR: {original_text}")
        else:
            print(f"   기존 OCR: (없음)")
        
        # Llama Vision 테스트
        print("   🦙 Llama3.2-Vision 테스트 중...")
        llama_result = ocr_with_llama_vision(img_path)
        
        if llama_result['success']:
            stats['llama']['success'] += 1
            stats['llama']['total_time'] += llama_result['time']
            stats['llama']['total_length'] += llama_result['length']
            print(f"      ✅ 성공 ({llama_result['time']:.2f}s, {llama_result['length']}자)")
            print(f"      결과: {llama_result['text'][:50]}..." if len(llama_result['text']) > 50 else f"      결과: {llama_result['text']}")
        else:
            stats['llama']['failed'] += 1
            print(f"      ❌ 실패: {llama_result.get('error', 'Unknown')}")
        
        # OpenAI Vision 테스트
        print("   🤖 OpenAI Vision 테스트 중...")
        openai_result = ocr_with_openai(img_path)
        
        if openai_result['success']:
            stats['openai']['success'] += 1
            stats['openai']['total_time'] += openai_result['time']
            stats['openai']['total_length'] += openai_result['length']
            print(f"      ✅ 성공 ({openai_result['time']:.2f}s, {openai_result['length']}자)")
            print(f"      결과: {openai_result['text'][:50]}..." if len(openai_result['text']) > 50 else f"      결과: {openai_result['text']}")
        else:
            stats['openai']['failed'] += 1
            print(f"      ❌ 실패: {openai_result.get('error', 'Unknown')}")
        
        results.append({
            'id': img_id,
            'original': original_text,
            'llama': llama_result,
            'openai': openai_result
        })
        
        print()
        time.sleep(1)
    
    # 최종 통계
    print("\n" + "="*80)
    print("📊 비교 결과")
    print("="*80 + "\n")
    
    print("🦙 **Llama3.2-Vision (11B)**")
    print(f"   성공: {stats['llama']['success']}/10")
    print(f"   실패: {stats['llama']['failed']}/10")
    if stats['llama']['success'] > 0:
        avg_time = stats['llama']['total_time'] / stats['llama']['success']
        avg_length = stats['llama']['total_length'] / stats['llama']['success']
        print(f"   평균 속도: {avg_time:.2f}초/건")
        print(f"   평균 길이: {avg_length:.0f}자")
    
    print("\n🤖 **OpenAI Vision (gpt-4o-mini)**")
    print(f"   성공: {stats['openai']['success']}/10")
    print(f"   실패: {stats['openai']['failed']}/10")
    if stats['openai']['success'] > 0:
        avg_time = stats['openai']['total_time'] / stats['openai']['success']
        avg_length = stats['openai']['total_length'] / stats['openai']['success']
        print(f"   평균 속도: {avg_time:.2f}초/건")
        print(f"   평균 길이: {avg_length:.0f}자")
    
    # 속도 비교
    if stats['llama']['success'] > 0 and stats['openai']['success'] > 0:
        llama_avg = stats['llama']['total_time'] / stats['llama']['success']
        openai_avg = stats['openai']['total_time'] / stats['openai']['success']
        
        print("\n⚡ **속도 비교:**")
        if llama_avg < openai_avg:
            print(f"   Llama가 {openai_avg/llama_avg:.1f}배 빠름")
        else:
            print(f"   OpenAI가 {llama_avg/openai_avg:.1f}배 빠름")
    
    print("\n" + "="*80)
    print("✅ 테스트 완료!")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
