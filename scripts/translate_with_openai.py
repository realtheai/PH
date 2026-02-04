"""
OpenAI API로 영어 콘텐츠를 한국어로 번역
"""
import os
import requests
import time
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class OpenAITranslator:
    def __init__(self, api_key: str, supabase_url: str, supabase_key: str):
        self.api_key = api_key
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        
        self.headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json"
        }
        
        print(f"✅ OpenAI API 키 로드 완료")
    
    def translate_to_korean(self, text: str, max_retries: int = 3) -> dict:
        """OpenAI GPT로 영어 → 한국어 번역"""
        if not text or len(text.strip()) < 10:
            return {'success': False, 'error': '텍스트가 너무 짧음'}
        
        for attempt in range(max_retries):
            try:
                url = "https://api.openai.com/v1/chat/completions"
                
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": "gpt-4o-mini",  # 저렴하고 빠른 모델
                    "messages": [
                        {
                            "role": "system",
                            "content": "당신은 전문 번역가입니다. 영어를 한국어로 자연스럽게 번역해주세요. 이미 한국어라면 그대로 출력하세요. 번역만 출력하고 다른 설명은 하지 마세요."
                        },
                        {
                            "role": "user",
                            "content": text[:2000]
                        }
                    ],
                    "temperature": 0.3,
                    "max_tokens": 2000
                }
                
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                
                if response.status_code == 429:
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 10
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
                
                if 'choices' in result and len(result['choices']) > 0:
                    translated = result['choices'][0]['message']['content'].strip()
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
        print(f"📰 뉴스 콘텐츠 번역 (OpenAI GPT-4o-mini)")
        if start_id > 0:
            print(f"   ID {start_id}부터 시작")
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
            time.sleep(1)  # OpenAI는 Rate Limit이 더 관대함
        
        print(f"\n{'='*70}")
        print(f"📊 뉴스 번역 완료")
        print(f"{'='*70}")
        print(f"   성공: {stats['success']}개")
        print(f"   실패: {stats['failed']}개")
        print(f"   스킵: {stats['skipped']}개")
        print(f"{'='*70}\n")
        
        return stats

def main():
    openai_key = os.getenv('OPENAI_API_KEY')
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not openai_key:
        print("❌ OPENAI_API_KEY가 없습니다!")
        return
    
    if not all([supabase_url, supabase_key]):
        print("❌ Supabase 환경 변수가 없습니다!")
        return
    
    translator = OpenAITranslator(
        api_key=openai_key,
        supabase_url=supabase_url,
        supabase_key=supabase_key
    )
    
    # 뉴스 번역 (처음부터 또는 특정 ID부터)
    stats = translator.translate_news(start_id=0)
    
    print("\n🎉 번역 완료!")

if __name__ == "__main__":
    main()
