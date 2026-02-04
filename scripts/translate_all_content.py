"""
Gemini API를 사용해서 영어 콘텐츠를 한국어로 번역
"""
import os
import requests
import time
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class GeminiTranslator:
    def __init__(self, api_keys: list, supabase_url: str, supabase_key: str, openai_key: str = None):
        self.api_keys = api_keys
        self.current_key_index = 0
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.openai_key = openai_key
        self.model = "gemini-2.5-flash"
        
        self.headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json"
        }
        
        print(f"✅ Gemini API 키 {len(self.api_keys)}개 로드")
        if openai_key:
            print(f"✅ OpenAI API 키 로드 (fallback 사용)")
    
    def get_next_api_key(self) -> str:
        """라운드 로빈 방식으로 API 키 순환"""
        key = self.api_keys[self.current_key_index]
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        return key
    
    def translate_with_openai(self, text: str) -> dict:
        """OpenAI로 번역 (fallback)"""
        if not self.openai_key:
            return {'success': False, 'error': 'OpenAI API 키 없음'}
        
        try:
            headers = {
                'Authorization': f'Bearer {self.openai_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': 'gpt-4o-mini',
                'messages': [
                    {'role': 'system', 'content': '당신은 전문 번역가입니다. 영어를 한국어로 자연스럽게 번역하세요. 이미 한국어라면 그대로 출력하세요.'},
                    {'role': 'user', 'content': f'다음 텍스트를 한국어로 번역하세요:\n\n{text[:2000]}'}
                ],
                'max_tokens': 2048,
                'temperature': 0.3
            }
            
            response = requests.post('https://api.openai.com/v1/chat/completions', 
                                    headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                translated = result['choices'][0]['message']['content'].strip()
                return {'success': True, 'translated': translated}
            else:
                return {'success': False, 'error': f'OpenAI API 오류: {response.status_code}'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def translate_to_korean(self, text: str, max_retries: int = 3) -> dict:
        """Gemini로 영어 → 한국어 번역 (실패시 OpenAI fallback)"""
        if not text or len(text.strip()) < 5:
            return {'success': False, 'error': '텍스트가 너무 짧음'}
        
        # 먼저 Gemini 시도
        for attempt in range(max_retries):
            try:
                api_key = self.get_next_api_key()
                url = f"https://generativelanguage.googleapis.com/v1/models/{self.model}:generateContent?key={api_key}"
                
                prompt = f"""다음 텍스트를 한국어로 자연스럽게 번역해주세요.
이미 한국어라면 그대로 출력하세요.
번역만 출력하고 다른 설명은 하지 마세요.

텍스트:
{text[:2000]}

번역:"""
                
                payload = {
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }],
                    "generationConfig": {
                        "temperature": 0.3,
                        "maxOutputTokens": 2048
                    }
                }
                
                response = requests.post(url, json=payload, timeout=30)
                
                if response.status_code == 429:
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 10
                        time.sleep(wait_time)
                        continue
                    # Gemini Rate limit → OpenAI로 전환
                    print(f"   ⚠️ Gemini Rate limit → OpenAI 사용")
                    return self.translate_with_openai(text)
                
                if response.status_code != 200:
                    if attempt < max_retries - 1:
                        time.sleep(5)
                        continue
                    # Gemini 실패 → OpenAI로 전환
                    print(f"   ⚠️ Gemini 실패 → OpenAI 사용")
                    return self.translate_with_openai(text)
                
                result = response.json()
                
                if 'candidates' in result and len(result['candidates']) > 0:
                    translated = result['candidates'][0]['content']['parts'][0]['text'].strip()
                    return {'success': True, 'translated': translated}
                else:
                    return {'success': False, 'error': '번역 결과 없음'}
            
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(5)
                    continue
                # Gemini 예외 → OpenAI로 전환
                print(f"   ⚠️ Gemini 오류 → OpenAI 사용")
                return self.translate_with_openai(text)
        
        # 모든 Gemini 시도 실패 → OpenAI로 전환
        print(f"   ⚠️ Gemini 최대 재시도 초과 → OpenAI 사용")
        return self.translate_with_openai(text)
    
    def translate_images(self):
        """phishing_images 테이블의 영어 텍스트 번역"""
        print(f"\n{'='*70}")
        print(f"🖼️  이미지 OCR 텍스트 번역")
        print(f"{'='*70}\n")
        
        # 번역이 필요한 데이터 조회 (영어 또는 translated_text가 NULL)
        url = f"{self.supabase_url}/rest/v1/phishing_images?select=id,ocr_text,language&or=(language.eq.en,translated_text.is.null)&limit=1000"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            print(f"❌ 데이터 조회 실패: {response.status_code}")
            return
        
        data = response.json()
        print(f"번역 대상: {len(data)}개\n")
        
        stats = {'success': 0, 'failed': 0, 'skipped': 0}
        
        for idx, item in enumerate(data, 1):
            item_id = item['id']
            ocr_text = item.get('ocr_text', '')
            language = item.get('language', '')
            
            print(f"[{idx}/{len(data)}] ID: {item_id}")
            
            # 텍스트가 없으면 스킵
            if not ocr_text or len(ocr_text.strip()) < 5:
                print(f"   ⚠️  텍스트 없음 - 스킵")
                stats['skipped'] += 1
                continue
            
            # 한국어 비율 확인
            korean_chars = sum(1 for c in ocr_text if '\uac00' <= c <= '\ud7a3')
            total_chars = len(ocr_text.replace(' ', '').replace('\n', ''))
            
            if total_chars > 0 and korean_chars / total_chars > 0.5:
                print(f"   ✅ 이미 한국어 (스킵)")
                # language 업데이트
                update_url = f"{self.supabase_url}/rest/v1/phishing_images?id=eq.{item_id}"
                requests.patch(update_url, headers=self.headers, json={'language': 'ko'})
                stats['skipped'] += 1
                continue
            
            # 번역 실행
            result = self.translate_to_korean(ocr_text)
            
            if result['success']:
                translated = result['translated']
                print(f"   ✅ 번역 완료: {len(translated)}자")
                
                # DB 업데이트
                update_url = f"{self.supabase_url}/rest/v1/phishing_images?id=eq.{item_id}"
                update_data = {
                    'translated_text': translated,
                    'language': 'ko',
                    'processed_at': datetime.now().isoformat()
                }
                
                update_response = requests.patch(update_url, headers=self.headers, json=update_data)
                
                if update_response.status_code in [200, 204]:
                    print(f"   💾 DB 업데이트 완료")
                    stats['success'] += 1
                else:
                    print(f"   ⚠️  DB 업데이트 실패")
                    stats['failed'] += 1
            else:
                print(f"   ❌ 번역 실패: {result.get('error')}")
                    stats['failed'] += 1
            
            print()
            time.sleep(2)  # Rate limiting (6개 키로 분당 90회 가능)
        
        print(f"\n{'='*70}")
        print(f"📊 이미지 번역 완료")
        print(f"{'='*70}")
        print(f"   성공: {stats['success']}개")
        print(f"   실패: {stats['failed']}개")
        print(f"   스킵: {stats['skipped']}개")
        print(f"{'='*70}\n")
    
    def translate_news(self):
        """phishing_news 테이블의 영어 텍스트 번역"""
        print(f"\n{'='*70}")
        print(f"📰 뉴스 콘텐츠 번역")
        print(f"{'='*70}\n")
        
        # 번역이 필요한 데이터 조회 (영어)
        # 최근 2일 내 영어 콘텐츠만 조회
        from datetime import datetime, timedelta
        two_days_ago = (datetime.now() - timedelta(days=2)).isoformat()
        url = f"{self.supabase_url}/rest/v1/phishing_news?select=id,content,original_language&original_language=eq.en&crawled_at=gte.{two_days_ago}&limit=1000"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            print(f"❌ 데이터 조회 실패: {response.status_code}")
            return
        
        data = response.json()
        print(f"번역 대상: {len(data)}개\n")
        
        if len(data) == 0:
            print("✅ 번역할 영어 뉴스가 없습니다!\n")
            return
        
        stats = {'success': 0, 'failed': 0, 'skipped': 0}
        
        for idx, item in enumerate(data, 1):
            item_id = item['id']
            content = item.get('content', '')
            
            print(f"[{idx}/{len(data)}] ID: {item_id}")
            
            # 텍스트가 없으면 스킵
            if not content or len(content.strip()) < 10:
                print(f"   ⚠️  콘텐츠 없음 - 스킵")
                stats['skipped'] += 1
                continue
            
            # 번역 실행
            result = self.translate_to_korean(content)
            
            if result['success']:
                translated = result['translated']
                print(f"   ✅ 번역 완료: {len(translated)}자")
                
                # DB 업데이트 (content를 번역본으로 교체)
                update_url = f"{self.supabase_url}/rest/v1/phishing_news?id=eq.{item_id}"
                update_data = {
                    'content': translated,
                    'original_language': 'ko'  # 번역 후 한국어로 변경
                }
                
                update_response = requests.patch(update_url, headers=self.headers, json=update_data)
                
                if update_response.status_code in [200, 204]:
                    print(f"   💾 DB 업데이트 완료")
                    stats['success'] += 1
                else:
                    print(f"   ⚠️  DB 업데이트 실패")
                    stats['failed'] += 1
            else:
                print(f"   ❌ 번역 실패: {result.get('error')}")
                    stats['failed'] += 1
            
            print()
            time.sleep(2)  # Rate limiting (6개 키로 분당 90회 가능)
        
        print(f"\n{'='*70}")
        print(f"📊 뉴스 번역 완료")
        print(f"{'='*70}")
        print(f"   성공: {stats['success']}개")
        print(f"   실패: {stats['failed']}개")
        print(f"   스킵: {stats['skipped']}개")
        print(f"{'='*70}\n")

def main():
    # API 키 로드
    api_keys = []
    for i in range(1, 10):
        if i == 1:
            key = os.getenv('GEMINI_API_KEY')
        else:
            key = os.getenv(f'GEMINI_API_KEY_{i}')
        
        if key:
            api_keys.append(key)
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if not api_keys:
        print("❌ GEMINI_API_KEY가 없습니다!")
        return
    
    if not all([supabase_url, supabase_key]):
        print("❌ Supabase 환경 변수가 없습니다!")
        return
    
    translator = GeminiTranslator(
        api_keys=api_keys,
        supabase_url=supabase_url,
        supabase_key=supabase_key,
        openai_key=openai_key
    )
    
    # 1. 이미지 번역
    translator.translate_images()
    
    # 2. 뉴스 번역
    translator.translate_news()
    
    print("\n🎉 전체 번역 완료!")

if __name__ == "__main__":
    main()
