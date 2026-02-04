"""
뉴스만 번역 (이미지는 이미 완료됨)
"""
import os
import requests
import time
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class NewsTranslator:
    def __init__(self, api_keys: list, supabase_url: str, supabase_key: str):
        self.api_keys = api_keys
        self.current_key_index = 0
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.model = "gemini-2.5-flash"
        
        self.headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json"
        }
        
        print(f"✅ API 키 {len(self.api_keys)}개 로드")
    
    def get_next_api_key(self) -> str:
        key = self.api_keys[self.current_key_index]
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        return key
    
    def translate_to_korean(self, text: str, max_retries: int = 3) -> dict:
        if not text or len(text.strip()) < 10:
            return {'success': False, 'error': '텍스트가 너무 짧음'}
        
        for attempt in range(max_retries):
            try:
                api_key = self.get_next_api_key()
                url = f"https://generativelanguage.googleapis.com/v1/models/{self.model}:generateContent?key={api_key}"
                
                prompt = f"""다음 영어 뉴스 기사를 한국어로 자연스럽게 번역해주세요.
이미 한국어라면 그대로 출력하세요.
번역만 출력하고 다른 설명은 하지 마세요.

원문:
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
                        wait_time = (attempt + 1) * 15
                        print(f"      ⏳ Rate limit - {wait_time}초 대기")
                        time.sleep(wait_time)
                        continue
                    return {'success': False, 'error': 'Rate limit'}
                
                if response.status_code != 200:
                    if attempt < max_retries - 1:
                        time.sleep(5)
                        continue
                    return {'success': False, 'error': f'API 오류: {response.status_code}'}
                
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
                return {'success': False, 'error': str(e)}
        
        return {'success': False, 'error': '최대 재시도 초과'}
    
    def translate_news(self, start_id: int = 0):
        """phishing_news 테이블의 영어 텍스트 번역"""
        print(f"\n{'='*70}")
        print(f"📰 뉴스 콘텐츠 번역 (ID {start_id}부터)")
        print(f"{'='*70}\n")
        
        # 번역이 필요한 데이터 조회
        if start_id > 0:
            url = f"{self.supabase_url}/rest/v1/phishing_news?select=id,content,original_language&original_language=eq.en&id=gte.{start_id}&order=id.asc&limit=1000"
        else:
            url = f"{self.supabase_url}/rest/v1/phishing_news?select=id,content,original_language&original_language=eq.en&order=id.asc&limit=1000"
        
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
            
            if not content or len(content.strip()) < 10:
                print(f"   ⚠️  콘텐츠 없음 - 스킵")
                stats['skipped'] += 1
                continue
            
            # 번역 실행
            result = self.translate_to_korean(content)
            
            if result['success']:
                translated = result['translated']
                print(f"   ✅ 번역 완료: {len(translated)}자")
                
                # DB 업데이트
                update_url = f"{self.supabase_url}/rest/v1/phishing_news?id=eq.{item_id}"
                update_data = {
                    'content': translated,
                    'original_language': 'ko'
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
            time.sleep(3)  # 안전하게 3초 대기
        
        print(f"\n{'='*70}")
        print(f"📊 뉴스 번역 완료")
        print(f"{'='*70}")
        print(f"   성공: {stats['success']}개")
        print(f"   실패: {stats['failed']}개")
        print(f"   스킵: {stats['skipped']}개")
        print(f"{'='*70}\n")

def main():
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
    
    if not api_keys:
        print("❌ GEMINI_API_KEY가 없습니다!")
        return
    
    if not all([supabase_url, supabase_key]):
        print("❌ Supabase 환경 변수가 없습니다!")
        return
    
    translator = NewsTranslator(
        api_keys=api_keys,
        supabase_url=supabase_url,
        supabase_key=supabase_key
    )
    
    # 뉴스 번역 (ID 3240부터 재개)
    translator.translate_news(start_id=3240)
    
    print("\n🎉 뉴스 번역 완료!")

if __name__ == "__main__":
    main()
