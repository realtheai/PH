#!/usr/bin/env python3
"""
하이브리드 OCR 전략: OpenAI + Ollama 백업
"""
import os
import requests
import base64
import time
from dotenv import load_dotenv

load_dotenv()

OPENAI_KEY = os.getenv('OPENAI_API_KEY')

def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

def ocr_with_openai(image_path):
    """OpenAI Vision OCR (개선된 프롬프트)"""
    try:
        base64_image = encode_image(image_path)
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENAI_KEY}"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Perform OCR (Optical Character Recognition) on this image.
Extract all visible text exactly as it appears.
Languages: Korean (한글), English
Format: Plain text only"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        }
                    ]
                }],
                "max_tokens": 1024,
                "temperature": 0.1
            },
            timeout=60
        )
        
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content'].strip()
            
            # 거부 패턴 감지
            rejection_keywords = [
                "추출할 수 없습니다", "cannot", "can't", "unable",
                "I'm sorry", "죄송", "도구를 사용하세요"
            ]
            
            for keyword in rejection_keywords:
                if keyword in content.lower():
                    return None, "rejected"
            
            # 너무 짧으면 실패로 간주
            if len(content) < 10:
                return None, "too_short"
            
            return content, "success"
        else:
            return None, f"api_error_{response.status_code}"
            
    except Exception as e:
        return None, f"exception_{str(e)[:30]}"

def ocr_with_ollama(image_path):
    """Ollama glm-ocr 백업"""
    try:
        base64_image = encode_image(image_path)
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "glm-ocr",
                "prompt": "Text Recognition (Korean and English only, output in original language):",
                "images": [base64_image],
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 2000
                }
            },
            timeout=120
        )
        
        if response.status_code == 200:
            content = response.json().get('response', '').strip()
            
            # 너무 짧거나 비정상이면 실패
            if len(content) < 5:
                return None, "too_short"
            
            # 중국어 반복 패턴 감지
            if content.count('中文') > 3 or content.count('识别') > 3:
                return None, "chinese_hallucination"
            
            return content, "success"
        else:
            return None, f"api_error_{response.status_code}"
            
    except Exception as e:
        return None, f"exception_{str(e)[:30]}"

def hybrid_ocr(image_path, verbose=True):
    """
    하이브리드 OCR 전략
    1차: OpenAI Vision (빠르고 정확)
    2차: Ollama glm-ocr (백업)
    """
    start_time = time.time()
    
    if verbose:
        print(f"\n📸 {os.path.basename(image_path)}")
        print("-" * 80)
    
    # 1차: OpenAI 시도
    result, status = ocr_with_openai(image_path)
    
    if status == "success":
        elapsed = time.time() - start_time
        if verbose:
            print(f"✅ OpenAI 성공 ({elapsed:.1f}초)")
            print(f"   추출 길이: {len(result)}자")
            print(f"   내용: {result[:100]}...")
        return {
            'text': result,
            'method': 'openai',
            'status': 'success',
            'time': elapsed
        }
    
    if verbose:
        print(f"⚠️ OpenAI 실패: {status}")
        print(f"   → Ollama 백업 시도...")
    
    # 2차: Ollama 백업
    ollama_start = time.time()
    result, status = ocr_with_ollama(image_path)
    
    if status == "success":
        elapsed = time.time() - start_time
        if verbose:
            print(f"✅ Ollama 성공 ({time.time() - ollama_start:.1f}초)")
            print(f"   추출 길이: {len(result)}자")
            print(f"   내용: {result[:100]}...")
        return {
            'text': result,
            'method': 'ollama',
            'status': 'success',
            'time': elapsed
        }
    
    # 둘 다 실패
    elapsed = time.time() - start_time
    if verbose:
        print(f"❌ 모두 실패 ({elapsed:.1f}초)")
        print(f"   Ollama 상태: {status}")
    
    return {
        'text': None,
        'method': 'none',
        'status': 'failed',
        'time': elapsed
    }

# 테스트
if __name__ == "__main__":
    test_images = [
        "data/images/phishing/결제_알림_피싱_문자_17.jpg",  # OpenAI 성공
        "data/images/phishing/스미싱_문자_사례_2.jpg",      # OpenAI 거부
        "data/images/phishing/스미싱_문자_사례_3.jpg",      # OpenAI 성공
        "data/images/phishing/스미싱_문자_사례_9.jpg",      # OpenAI 부분 성공
    ]
    
    print("\n" + "="*100)
    print("🧪 하이브리드 OCR 전략 테스트")
    print("="*100)
    
    results = []
    for img_path in test_images:
        if os.path.exists(img_path):
            result = hybrid_ocr(img_path, verbose=True)
            results.append(result)
    
    # 통계
    print("\n" + "="*100)
    print("📊 결과 통계")
    print("="*100)
    
    openai_success = sum(1 for r in results if r['method'] == 'openai')
    ollama_success = sum(1 for r in results if r['method'] == 'ollama')
    failed = sum(1 for r in results if r['method'] == 'none')
    avg_time = sum(r['time'] for r in results) / len(results)
    
    print(f"\n총 테스트: {len(results)}개")
    print(f"  ✅ OpenAI 성공: {openai_success}개")
    print(f"  ✅ Ollama 백업 성공: {ollama_success}개")
    print(f"  ❌ 완전 실패: {failed}개")
    print(f"  ⏱️ 평균 시간: {avg_time:.1f}초")
    print(f"\n성공률: {(openai_success + ollama_success) / len(results) * 100:.1f}%")
    
    print("\n" + "="*100)
    print("✅ 테스트 완료!")
    print("="*100)
