"""
REAL_CASE 피싱 유형 재분류
- REAL_CASE로 분류된 데이터에 대해 피싱 유형(phishing_type)만 분류
"""
import os
import requests
import time
import json
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# 피싱 유형 분류 프롬프트
TYPE_CLASSIFICATION_PROMPT = """당신은 피싱 유형 분류 전문가입니다.

**Task**: 입력된 피싱 사례를 적절한 유형으로 분류하세요.

**피싱 유형**:
1. 가족사칭 - 자녀, 부모, 친척 등을 사칭
2. 공공기관사칭 - 경찰, 검찰, 금감원, 구청, 시청 등
3. 지인사칭 - 친구, 동료 등을 사칭
4. 부고/경조사 - 부고, 결혼, 돌잔치 등을 빙자
5. 정부지원금 - 코로나 지원금, 재난지원금 등
6. 금융/결제사기 - 대출, 카드, 계좌 등
7. 택배/배송사기 - CJ, 롯데택배 등 사칭
8. 투자사기 - 코인, 주식, 골드바 등
9. 기타 - 위 유형에 해당하지 않는 경우

**출력 형식**: JSON만 출력하세요.
{
  "phishing_type": "유형 이름"
}

**예시**:

입력: 한국관광공사 임직원 사칭 노쇼 사기 주의보. 계약을 미끼로 선입금을 요구하는 수법이 기승을 부리고 있다.
출력: {"phishing_type": "공공기관사칭"}

입력: 골드바 보이스피싱 주의보. 인천경찰청이 귀금속업소 범죄 피해 예방 활동을 벌이고 있다.
출력: {"phishing_type": "투자사기"}

입력: 엄마 나야. 휴대폰 고장나서 친구 폰으로 연락해. 급한 일 있어서 지금 당장 200만원 입금 좀 해줄래?
출력: {"phishing_type": "가족사칭"}

입력: 코트라 사칭 피싱 범죄 주의보. 코트라 직원을 사칭해 거래기업을 상대로 금전을 요구하는 수법이 급증하고 있다.
출력: {"phishing_type": "공공기관사칭"}

**이제 다음 텍스트를 분석하세요**:
"""

class PhishingTypeClassifier:
    def __init__(self, gemini_keys: list, openai_key: str, supabase_url: str, supabase_key: str):
        self.gemini_keys = gemini_keys
        self.openai_key = openai_key
        self.current_gemini_index = 0
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.model_gemini = "gemini-2.5-flash"
        
        self.headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json"
        }
        
        print(f"✅ Gemini API 키 {len(self.gemini_keys)}개 로드")
        print(f"✅ OpenAI API 키 로드 (폴백용)")
    
    def get_next_gemini_key(self) -> str:
        key = self.gemini_keys[self.current_gemini_index]
        self.current_gemini_index = (self.current_gemini_index + 1) % len(self.gemini_keys)
        return key
    
    def classify_type_with_gemini(self, text: str, max_retries: int = 2) -> dict:
        """Gemini로 피싱 유형 분류"""
        for attempt in range(max_retries):
            try:
                api_key = self.get_next_gemini_key()
                url = f"https://generativelanguage.googleapis.com/v1/models/{self.model_gemini}:generateContent?key={api_key}"
                
                prompt = f"{TYPE_CLASSIFICATION_PROMPT}\n\n입력: {text[:1000]}\n\n출력 (JSON만):"
                
                payload = {
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }],
                    "generationConfig": {
                        "temperature": 0.1,
                        "maxOutputTokens": 256
                    }
                }
                
                response = requests.post(url, json=payload, timeout=20)
                
                # Rate Limit 발생 시 Exponential Backoff
                if response.status_code == 429:
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt)
                        time.sleep(wait_time)
                        continue
                    else:
                        return {'success': False, 'error': 'Rate limit', 'use_openai': True}
                
                if response.status_code != 200:
                    return {'success': False, 'error': f'API 오류: {response.status_code}', 'use_openai': True}
                
                result = response.json()
                
                if 'candidates' in result and len(result['candidates']) > 0:
                    text_result = result['candidates'][0]['content']['parts'][0]['text'].strip()
                    
                    # JSON 추출
                    if '```json' in text_result:
                        text_result = text_result.split('```json')[1].split('```')[0].strip()
                    elif '```' in text_result:
                        text_result = text_result.split('```')[1].split('```')[0].strip()
                    
                    classification = json.loads(text_result)
                    return {'success': True, 'classification': classification}
                else:
                    return {'success': False, 'error': '결과 없음', 'use_openai': True}
            
            except json.JSONDecodeError:
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                else:
                    return {'success': False, 'error': 'JSON 파싱 실패', 'use_openai': True}
            
            except Exception as e:
                return {'success': False, 'error': str(e), 'use_openai': True}
        
        return {'success': False, 'error': 'Max retries', 'use_openai': True}
    
    def classify_type_with_openai(self, text: str) -> dict:
        """OpenAI로 피싱 유형 분류"""
        try:
            url = "https://api.openai.com/v1/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {self.openai_key}",
                "Content-Type": "application/json"
            }
            
            messages = [
                {"role": "system", "content": TYPE_CLASSIFICATION_PROMPT},
                {"role": "user", "content": text[:1000]}
            ]
            
            payload = {
                "model": "gpt-4o-mini",
                "messages": messages,
                "temperature": 0.1,
                "max_tokens": 256,
                "response_format": {"type": "json_object"}
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=20)
            
            if response.status_code != 200:
                return {'success': False, 'error': f'API 오류: {response.status_code}'}
            
            result = response.json()
            
            if 'choices' in result and len(result['choices']) > 0:
                text_result = result['choices'][0]['message']['content'].strip()
                classification = json.loads(text_result)
                return {'success': True, 'classification': classification}
            else:
                return {'success': False, 'error': '결과 없음'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def classify_phishing_type(self, text: str) -> dict:
        """피싱 유형 분류 (Gemini 먼저, 실패시 OpenAI)"""
        # 1. Gemini 시도
        result = self.classify_type_with_gemini(text)
        
        if result['success']:
            return {'success': True, 'classification': result['classification'], 'model': 'gemini'}
        
        # 2. OpenAI 폴백
        if result.get('use_openai'):
            result = self.classify_type_with_openai(text)
            
            if result['success']:
                return {'success': True, 'classification': result['classification'], 'model': 'openai'}
        
        return {'success': False, 'error': result.get('error', 'Unknown')}
    
    def reclassify_real_cases(self, limit: int = 500):
        """REAL_CASE 피싱 유형 재분류"""
        print(f"\n{'='*70}")
        print(f"🎯 REAL_CASE 피싱 유형 재분류")
        print(f"{'='*70}\n")
        
        # phishing_type이 NULL인 REAL_CASE 조회
        # 최근 2일 내 REAL_CASE 중 피싱 유형이 없는 데이터만 조회 (최신 데이터부터)
        from datetime import datetime, timedelta
        two_days_ago = (datetime.now() - timedelta(days=2)).isoformat()
        url = f"{self.supabase_url}/rest/v1/phishing_news?select=id,title,content&category=eq.REAL_CASE&phishing_type=is.null&crawled_at=gte.{two_days_ago}&order=id.desc&limit={limit}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            print(f"❌ 데이터 조회 실패: {response.status_code}")
            return
        
        data = response.json()
        print(f"재분류 대상: {len(data)}개\n")
        
        if len(data) == 0:
            print("✅ 재분류할 데이터가 없습니다!\n")
            return
        
        stats = {'success': 0, 'failed': 0, 'gemini': 0, 'openai': 0}
        
        for idx, item in enumerate(data, 1):
            item_id = item['id']
            title = item.get('title', '')
            content = item.get('content', '')
            
            text_to_classify = f"{title}\n\n{content}"
            
            print(f"[{idx}/{len(data)}] ID: {item_id}")
            print(f"   제목: {title[:50]}...")
            
            # 유형 분류 실행
            result = self.classify_phishing_type(text_to_classify)
            
            if result['success']:
                classification = result['classification']
                model_used = result['model']
                phishing_type = classification.get('phishing_type', '기타')
                
                print(f"   ✅ 분류 완료 ({model_used})")
                print(f"      유형: {phishing_type}")
                
                # DB 업데이트
                update_url = f"{self.supabase_url}/rest/v1/phishing_news?id=eq.{item_id}"
                update_data = {
                    'phishing_type': phishing_type,
                    'processed_at': datetime.now().isoformat()
                }
                
                update_response = requests.patch(update_url, headers=self.headers, json=update_data)
                
                if update_response.status_code in [200, 204]:
                    print(f"      💾 DB 업데이트 완료")
                    stats['success'] += 1
                    if model_used == 'gemini':
                        stats['gemini'] += 1
                    else:
                        stats['openai'] += 1
                else:
                    print(f"      ⚠️  DB 업데이트 실패")
                    stats['failed'] += 1
            else:
                print(f"   ❌ 분류 실패: {result.get('error')}")
                stats['failed'] += 1
            
            print()
            time.sleep(1.5)
        
        print(f"\n{'='*70}")
        print(f"📊 재분류 완료")
        print(f"{'='*70}")
        print(f"   성공: {stats['success']}개")
        print(f"   실패: {stats['failed']}개")
        print(f"   Gemini 사용: {stats['gemini']}개")
        print(f"   OpenAI 사용: {stats['openai']}개")
        print(f"{'='*70}\n")

def main():
    # API 키 로드
    gemini_keys = []
    for i in range(1, 10):
        if i == 1:
            key = os.getenv('GEMINI_API_KEY')
        else:
            key = os.getenv(f'GEMINI_API_KEY_{i}')
        
        if key:
            gemini_keys.append(key)
    
    openai_key = os.getenv('OPENAI_API_KEY')
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not gemini_keys and not openai_key:
        print("❌ API 키가 없습니다!")
        return
    
    if not all([supabase_url, supabase_key]):
        print("❌ Supabase 환경 변수가 없습니다!")
        return
    
    classifier = PhishingTypeClassifier(
        gemini_keys=gemini_keys if gemini_keys else [],
        openai_key=openai_key,
        supabase_url=supabase_url,
        supabase_key=supabase_key
    )
    
    # REAL_CASE 피싱 유형 재분류 (500개씩)
    classifier.reclassify_real_cases(limit=500)
    
    print("\n🎉 재분류 완료!")

if __name__ == "__main__":
    main()
