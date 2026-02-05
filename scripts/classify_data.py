"""
Gemini/OpenAI를 사용한 데이터 분류
- Gemini 먼저 시도, 실패시 OpenAI 사용
"""
import os
import requests
import time
import json
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# 분류 프롬프트 및 Few-shot 예시
SYSTEM_PROMPT = """당신은 대한민국 최고의 보이스피싱 및 스미싱 범죄 분석 전문가입니다.

**Task**: 입력된 텍스트를 분석하여 부모님을 보호하기 위한 보안 DB용 데이터를 추출하세요.

**분석 가이드라인**:

1. **판단**: 해당 텍스트가 RAG 시스템에서 활용 가능한 피싱 정보를 포함하는지 판단하세요.
   - **REAL_CASE**: 구체적인 피싱 수법, 타겟, 키워드가 포함된 정보 (RAG 활용 가능)
     * ✅ 실제 피싱 문자/대화 원문
     * ✅ 구체적인 사칭 대상 (예: "한국관광공사 사칭", "코트라 직원 사칭")
     * ✅ 구체적인 수법 설명 (예: "골드바 보이스피싱", "노쇼 사기로 선입금 요구")
     * ✅ 구체적인 키워드 (예: "김무현", "계약금", "선입금")
     * → 사용자가 관련 키워드를 포함한 메시지를 받으면 이 정보로 경고 가능!
   - **NEWS**: 추상적인 통계나 캠페인 소식으로 RAG에서 활용 불가
     * 예: "보이스피싱 375건 접수" (통계만, 수법/타겟 없음)
     * 예: "피싱 예방 캠페인 실시" (행사 소식만)
     * 예: "수법이 정교해지고 있다" (추상적 설명만)
   - **NOISE**: 피싱과 무관한 내용

2. **수법 분류**: 다음 중 하나로 분류하세요.
   - 가족사칭
   - 공공기관사칭 (경찰, 검찰, 금감원 등)
   - 지인사칭
   - 부고/경조사
   - 정부지원금
   - 금융/결제사기
   - 택배/배송사기
   - 투자사기
   - 기타

3. **핵심 문구 추출**: 범죄자가 실제로 사용하는 핵심 문장이나 키워드를 뽑아내세요.
   (예: "엄마 나 폰 고장났어", "액정 수리비 입금해줘")

4. **타겟별 맞춤 요약**: summary 필드에는 반드시 다음을 포함하세요:
   - 수법의 핵심 구조
   - **해당 타겟이 속기 쉬운 이유**
     * 부모님: "자녀의 다급한 목소리", "공공기관 권위에 겁먹음"
     * 청년: "택배/쇼핑몰 사칭", "투자 수익 유혹"
     * 일반: "금융거래 편의성", "정부지원금 놓칠까봐"
   - 대응 방법 (예: "전화번호를 직접 확인", "절대 먼저 송금 금지")

5. **변종 문구 생성**: key_phrases에는 실제 문구 + 변종 가능성 높은 유사 문구를 모두 포함하세요.
   (예: "엄마 나야" → "엄마", "나 OOO야", "아빠 나 폰 고장")

6. **위험도**: 1(낮음) ~ 5(매우 위험)로 책정하세요.

7. **타겟 대상**: 부모님/일반/청년 중 선택

**출력 형식**: JSON만 출력하세요. 다른 설명은 하지 마세요.
{
  "is_phishing": "REAL_CASE" | "NEWS" | "NOISE",
  "category": "string or null",
  "summary": "수법 요약 + [타겟별] 속기 쉬운 이유 + 대응 방법",
  "key_phrases": ["실제문구1", "실제문구2", "변종문구1", "변종문구2"],
  "danger_level": 1-5,
  "target_audience": "부모님" | "일반" | "청년"
}"""

FEW_SHOT_EXAMPLES = [
    {
        "input": "엄마 나야. 휴대폰 고장나서 친구 폰으로 연락해. 급한 일 있어서 지금 당장 200만원 입금 좀 해줄래? 계좌번호는 국민은행 123-456-789012야.",
        "output": {
            "is_phishing": "REAL_CASE",
            "category": "가족사칭",
            "summary": "자녀를 사칭하여 휴대폰 고장을 핑계로 급전 요구. **부모님이 속기 쉬운 이유**: 자녀의 다급한 메시지에 당황하고, '친구 폰 사용'이라는 설명으로 전화 확인을 회피함. **대응 방법**: 반드시 자녀의 원래 전화번호로 직접 통화 확인. 먼저 송금 절대 금지.",
            "key_phrases": ["엄마 나야", "아빠 나야", "나 OOO야", "휴대폰 고장", "폰 고장났어", "친구 폰으로 연락", "급한 일", "당장 입금", "200만원 입금", "계좌번호"],
            "danger_level": 5,
            "target_audience": "부모님"
        }
    },
    {
        "input": "서울경찰청입니다. 귀하의 명의로 대포통장이 개설되어 금융범죄에 연루되었습니다. 조사를 위해 금융감독원 안전계좌로 전 재산을 이체하셔야 합니다. 02-1234-5678로 연락주세요.",
        "output": {
            "is_phishing": "REAL_CASE",
            "category": "공공기관사칭",
            "summary": "경찰·검찰을 사칭하여 대포통장 연루를 명목으로 '안전계좌'로 전 재산 이체 요구. **부모님이 속기 쉬운 이유**: 공공기관의 권위에 겁먹고, '범죄 연루'라는 말에 패닉 상태가 됨. **대응 방법**: 경찰·검찰은 전화로 돈을 요구하지 않음. 112로 즉시 신고.",
            "key_phrases": ["서울경찰청", "검찰청", "금융감독원", "대포통장 개설", "금융범죄 연루", "범죄에 연루", "안전계좌로 이체", "전 재산 이체", "조사를 위해", "02-", "050-"],
            "danger_level": 5,
            "target_audience": "부모님"
        }
    },
    {
        "input": "[Web발신] CJ대한통운입니다. 고객님의 택배가 주소 불명으로 배송 실패했습니다. 재배송을 원하시면 https://cj-track.xyz 에서 주소를 재확인하세요.",
        "output": {
            "is_phishing": "REAL_CASE",
            "category": "택배/배송사기",
            "summary": "택배 배송 실패를 가장한 스미싱. 의심스러운 URL 클릭 유도로 개인정보 탈취 및 악성코드 설치 시도. **일반인이 속기 쉬운 이유**: 온라인 쇼핑 증가로 실제 택배를 자주 받고, 주소 불명 메시지에 당황하여 빠르게 클릭함. **대응 방법**: 택배사 공식 앱에서 직접 확인. 의심스러운 링크는 절대 클릭 금지.",
            "key_phrases": ["CJ대한통운", "롯데택배", "우체국택배", "주소 불명", "배송 실패", "배송불가", "재배송", "주소 재확인", "링크 클릭", "Web발신"],
            "danger_level": 4,
            "target_audience": "일반"
        }
    },
    {
        "input": "안녕하세요. 정부 코로나19 지원금 미신청자에게 100만원을 지급합니다. 아래 링크에서 신청하세요. https://gov-support.kr",
        "output": {
            "is_phishing": "REAL_CASE",
            "category": "정부지원금",
            "summary": "정부 지원금을 빙자한 스미싱. 가짜 정부 사이트로 유도하여 개인정보 및 금융정보 탈취. **일반인이 속기 쉬운 이유**: '100만원 지원금'이라는 실제 정부 정책과 혼동하고, '미신청자'라는 말에 놓칠까봐 조급해짐. **대응 방법**: 정부 지원금은 공식 사이트(gov.kr)에서만 신청. 의심스러운 링크는 절대 클릭 금지.",
            "key_phrases": ["정부 지원금", "코로나19 지원금", "미신청자", "100만원 지급", "긴급재난지원금", "아래 링크", "신청하세요", "gov-support", "kr 사칭"],
            "danger_level": 5,
            "target_audience": "일반"
        }
    },
    {
        "input": "🔥 월 수익률 300% 보장! 코인 자동매매 프로그램 무료 체험. 카톡 abc123으로 '투자'라고 보내주세요. 선착순 100명 한정!",
        "output": {
            "is_phishing": "REAL_CASE",
            "category": "투자사기",
            "summary": "고수익을 미끼로 한 투자사기. 가짜 자동매매 프로그램으로 유도하여 투자금 편취 또는 개인정보 탈취. **청년층이 속기 쉬운 이유**: 코인 투자에 관심이 많고, '월 300% 수익'이라는 과장된 수익률에 현혹됨. '선착순 한정'이라는 조급함 유발. **대응 방법**: 비정상적으로 높은 수익률은 100% 사기. 금융감독원 등록 여부 확인 필수.",
            "key_phrases": ["월 수익률 300%", "보장", "코인 자동매매", "무료 체험", "선착순 한정", "카톡", "투자", "고수익"],
            "danger_level": 5,
            "target_audience": "청년"
        }
    },
    {
        "input": "경찰청은 오늘 보이스피싱 예방을 위한 캠페인을 실시했다. 경찰 관계자는 '전화로 돈을 요구하면 100% 사기'라며 주의를 당부했다.",
        "output": {
            "is_phishing": "NEWS",
            "category": None,
            "summary": "보이스피싱 예방 캠페인 뉴스. 실제 사례나 구체적 수법 없음. 단순 예방 홍보성 기사.",
            "key_phrases": [],
            "danger_level": 1,
            "target_audience": "일반"
        }
    },
    {
        "input": "지난해 서울시에 공무원 사칭 상담 375건이 접수됐다. 기관사칭형 보이스피싱 피해액이 약 1조 원에 달한다. 최근 수법이 정교해지고 있다.",
        "output": {
            "is_phishing": "NEWS",
            "category": None,
            "summary": "보이스피싱 통계 뉴스. 구체적인 수법이나 타겟 키워드 없음. RAG 활용 불가.",
            "key_phrases": [],
            "danger_level": 1,
            "target_audience": "일반"
        }
    },
    {
        "input": "한국관광공사 임직원 사칭 노쇼 사기 주의보. 계약을 미끼로 선입금을 요구하는 수법이 기승을 부리고 있다. 한국관광공사는 '선입금 요구는 모두 사기'라고 밝혔다.",
        "output": {
            "is_phishing": "REAL_CASE",
            "category": "공공기관사칭",
            "summary": "한국관광공사 사칭 노쇼 사기. 계약 명목으로 선입금 요구. **일반인이 속기 쉬운 이유**: 공공기관 이름을 사용해 신뢰를 얻음. **대응 방법**: 한국관광공사는 선입금을 요구하지 않음. 공식 채널로 확인 필수.",
            "key_phrases": ["한국관광공사", "관광공사", "임직원", "노쇼", "계약", "선입금 요구", "선입금"],
            "danger_level": 4,
            "target_audience": "일반"
        }
    },
    {
        "input": "A씨는 어제 문자를 받았다. '엄마, 나 폰 고장났어. 급한 일 있어서 200만원 입금 부탁해. 계좌는 국민은행 123-456-789012야.' A씨는 이를 의심하고 경찰에 신고했다.",
        "output": {
            "is_phishing": "REAL_CASE",
            "category": "가족사칭",
            "summary": "자녀를 사칭한 급전 요구 문자. 실제 피싱 문자 원문이 인용됨. **일반인이 속기 쉬운 이유**: 자녀의 긴급 상황으로 위장하여 당황하게 만듦. **대응 방법**: 자녀에게 직접 전화로 확인. 먼저 송금 절대 금지.",
            "key_phrases": ["엄마", "나 폰 고장", "급한 일", "200만원 입금", "계좌는"],
            "danger_level": 5,
            "target_audience": "부모님"
        }
    },
    {
        "input": "합천군에 공무원 사칭 보이스피싱 사례가 발생했다. 최근 군청 행정전화번호를 도용해 '김무현'이라는 이름으로 기획예산담당관 소속 공무원인 것처럼 속이고, 여러 주민에게 반복적으로 전화를 걸었다. 일부 통화에서는 계약이나 업무 협조를 빌미로 접근한 뒤 금전 요구로 이어졌다.",
        "output": {
            "is_phishing": "REAL_CASE",
            "category": "공공기관사칭",
            "summary": "군청 공무원을 사칭한 보이스피싱. 실제 사례(이름, 부서, 수법)가 구체적으로 설명됨. **일반인이 속기 쉬운 이유**: 공공기관 행정전화로 걸려와 신뢰하게 됨. **대응 방법**: 공공기관은 전화로 금전 요구하지 않음. 해당 기관에 직접 확인.",
            "key_phrases": ["김무현", "군청", "기획예산담당관", "행정전화", "계약", "업무 협조", "금전 요구"],
            "danger_level": 5,
            "target_audience": "일반"
        }
    },
    {
        "input": "골드바 보이스피싱 주의보. 인천경찰청이 귀금속업소 범죄 피해 예방 활동을 벌이고 있다.",
        "output": {
            "is_phishing": "REAL_CASE",
            "category": "금융/결제사기",
            "summary": "골드바 관련 보이스피싱. **일반인이 속기 쉬운 이유**: 골드바 투자나 매매를 미끼로 신뢰를 얻음. **대응 방법**: 전화로 골드바 거래 유도는 사기 가능성 높음. 공식 귀금속 업체 직접 확인.",
            "key_phrases": ["골드바", "귀금속", "귀금속업소"],
            "danger_level": 4,
            "target_audience": "일반"
        }
    },
    {
        "input": "코트라 사칭 피싱 범죄 주의보. 코트라 직원을 사칭해 거래기업을 상대로 금전을 요구하는 수법이 급증하고 있다.",
        "output": {
            "is_phishing": "REAL_CASE",
            "category": "공공기관사칭",
            "summary": "코트라(한국무역투자진흥공사) 직원 사칭 피싱. 거래기업 대상으로 금전 요구. **일반인이 속기 쉬운 이유**: 코트라라는 공공기관 이름으로 신뢰를 얻음. **대응 방법**: 코트라는 전화로 금전 요구하지 않음. 공식 채널로 확인.",
            "key_phrases": ["코트라", "KOTRA", "한국무역투자진흥공사", "거래기업", "금전 요구"],
            "danger_level": 4,
            "target_audience": "일반"
        }
    },
    {
        "input": "오늘 날씨가 맑고 화창합니다. 서울 최고 기온은 25도입니다.",
        "output": {
            "is_phishing": "NOISE",
            "category": None,
            "summary": "피싱과 무관한 날씨 정보",
            "key_phrases": [],
            "danger_level": 1,
            "target_audience": "일반"
        }
    }
]

class DataClassifier:
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
    
    def classify_with_gemini(self, text: str, max_retries: int = 2) -> dict:
        """Gemini로 분류 시도 (JSON Mode + Exponential Backoff)"""
        for attempt in range(max_retries):
            try:
                api_key = self.get_next_gemini_key()
                url = f"https://generativelanguage.googleapis.com/v1/models/{self.model_gemini}:generateContent?key={api_key}"
                
                # Few-shot 예시 포함
                prompt = f"""{SYSTEM_PROMPT}

**Few-shot 예시**:

"""
                for ex in FEW_SHOT_EXAMPLES:
                    prompt += f"입력: {ex['input']}\n출력: {json.dumps(ex['output'], ensure_ascii=False)}\n\n"
                
                prompt += f"""**이제 다음 텍스트를 분석하세요**:

입력: {text[:1500]}

출력 (JSON만):"""
                
                payload = {
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }],
                    "generationConfig": {
                        "temperature": 0.1,
                        "maxOutputTokens": 1024
                        # REST API v1은 responseMimeType 미지원, 프롬프트로 JSON 유도
                    }
                }
                
                response = requests.post(url, json=payload, timeout=30)
                
                # Rate Limit 발생 시 Exponential Backoff
                if response.status_code == 429:
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt)  # 1초, 2초
                        print(f"      ⏳ Rate limit. {wait_time}초 후 재시도...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return {'success': False, 'error': 'Rate limit', 'use_openai': True}
                
                if response.status_code != 200:
                    return {'success': False, 'error': f'API 오류: {response.status_code}', 'use_openai': True}
                
                result = response.json()
                
                if 'candidates' in result and len(result['candidates']) > 0:
                    text_result = result['candidates'][0]['content']['parts'][0]['text'].strip()
                    
                    # JSON Mode 사용 시 바로 파싱 가능
                    classification = json.loads(text_result)
                    return {'success': True, 'classification': classification}
                else:
                    return {'success': False, 'error': '결과 없음', 'use_openai': True}
            
            except json.JSONDecodeError as e:
                # JSON 파싱 실패 시 재시도
                if attempt < max_retries - 1:
                    print(f"      ⚠️  JSON 파싱 실패. 재시도...")
                    time.sleep(1)
                    continue
                else:
                    return {'success': False, 'error': f'JSON 파싱 실패: {str(e)}', 'use_openai': True}
            
            except Exception as e:
                return {'success': False, 'error': str(e), 'use_openai': True}
        
        return {'success': False, 'error': 'Max retries reached', 'use_openai': True}
    
    def classify_with_openai(self, text: str) -> dict:
        """OpenAI로 분류"""
        try:
            url = "https://api.openai.com/v1/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {self.openai_key}",
                "Content-Type": "application/json"
            }
            
            # Few-shot 예시 구성
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            
            for ex in FEW_SHOT_EXAMPLES[:3]:  # 처음 3개만
                messages.append({"role": "user", "content": ex['input']})
                messages.append({"role": "assistant", "content": json.dumps(ex['output'], ensure_ascii=False)})
            
            messages.append({"role": "user", "content": text[:1500]})
            
            payload = {
                "model": "gpt-4o-mini",
                "messages": messages,
                "temperature": 0.1,
                "max_tokens": 1024,
                "response_format": {"type": "json_object"}
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
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
    
    def classify_text(self, text: str) -> dict:
        """텍스트 분류 (Gemini 먼저, 실패시 OpenAI)"""
        # 1. Gemini 시도
        result = self.classify_with_gemini(text)
        
        if result['success']:
            return {'success': True, 'classification': result['classification'], 'model': 'gemini'}
        
        # 2. OpenAI 폴백
        if result.get('use_openai'):
            print(f"      🔄 Gemini 실패 → OpenAI 사용")
            result = self.classify_with_openai(text)
            
            if result['success']:
                return {'success': True, 'classification': result['classification'], 'model': 'openai'}
        
        return {'success': False, 'error': result.get('error', 'Unknown')}
    
    def classify_news_data(self, limit: int = 100):
        """phishing_news 데이터 분류"""
        print(f"\n{'='*70}")
        print(f"📰 뉴스 데이터 분류")
        print(f"{'='*70}\n")
        
        # 최근 2일 내 분류되지 않은 데이터 조회 (category가 NULL 또는 'NEWS')
        # 최신 데이터부터 처리 (order=id.desc)
        from datetime import datetime, timedelta
        two_days_ago = (datetime.now() - timedelta(days=2)).isoformat()
        url = f"{self.supabase_url}/rest/v1/phishing_news?select=id,title,content&or=(category.is.null,category.eq.NEWS)&crawled_at=gte.{two_days_ago}&order=id.desc&limit={limit}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            print(f"❌ 데이터 조회 실패: {response.status_code}")
            return
        
        data = response.json()
        print(f"분류 대상: {len(data)}개\n")
        
        if len(data) == 0:
            print("✅ 분류할 데이터가 없습니다!\n")
            return
        
        stats = {'success': 0, 'failed': 0, 'gemini': 0, 'openai': 0}
        
        for idx, item in enumerate(data, 1):
            item_id = item['id']
            title = item.get('title', '')
            content = item.get('content', '')
            
            text_to_classify = f"{title}\n\n{content}"
            
            print(f"[{idx}/{len(data)}] ID: {item_id}")
            print(f"   제목: {title[:50]}...")
            
            # 분류 실행
            result = self.classify_text(text_to_classify)
            
            if result['success']:
                classification = result['classification']
                model_used = result['model']
                
                print(f"   ✅ 분류 완료 ({model_used})")
                print(f"      Type: {classification['is_phishing']}")
                print(f"      Category: {classification.get('category', 'N/A')}")
                print(f"      Danger: {classification['danger_level']}/5")
                
                # DB 업데이트
                update_url = f"{self.supabase_url}/rest/v1/phishing_news?id=eq.{item_id}"
                update_data = {
                    'category': classification['is_phishing'],
                    'phishing_type': classification.get('category'),
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
            time.sleep(2)
        
        print(f"\n{'='*70}")
        print(f"📊 분류 완료")
        print(f"{'='*70}")
        print(f"   성공: {stats['success']}개")
        print(f"   실패: {stats['failed']}개")
        print(f"   Gemini 사용: {stats['gemini']}개")
        print(f"   OpenAI 사용: {stats['openai']}개")
        print(f"{'='*70}\n")
    
    def augment_phishing_data(self, limit: int = 10):
        """
        데이터 증강 (Augmentation)
        REAL_CASE로 분류된 데이터를 바탕으로 변종 문구를 생성하여 학습 데이터를 늘림
        """
        print(f"\n{'='*70}")
        print(f"🔄 데이터 증강 (Augmentation)")
        print(f"{'='*70}\n")
        
        # REAL_CASE로 분류된 데이터 조회
        url = f"{self.supabase_url}/rest/v1/phishing_news?select=id,title,content,category,phishing_type&category=eq.REAL_CASE&limit={limit}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            print(f"❌ 데이터 조회 실패: {response.status_code}")
            return
        
        data = response.json()
        print(f"증강 대상: {len(data)}개\n")
        
        if len(data) == 0:
            print("✅ 증강할 REAL_CASE 데이터가 없습니다!\n")
            return
        
        augmented_count = 0
        
        for idx, item in enumerate(data, 1):
            item_id = item['id']
            title = item.get('title', '')
            content = item.get('content', '')
            phishing_type = item.get('phishing_type', '')
            
            print(f"[{idx}/{len(data)}] ID: {item_id} ({phishing_type})")
            print(f"   원본: {title[:40]}...")
            
            # 증강 프롬프트
            augment_prompt = f"""다음은 실제 {phishing_type} 피싱 사례입니다:

제목: {title}
내용: {content[:500]}

**Task**: 이 수법을 바탕으로 **비슷한 변종 문구 5개**를 생성하세요.
- 핵심 수법은 유지하되, 표현을 다르게
- 부모님이 속을 만한 현실적인 변종
- 각 변종은 한 문장으로 간결하게

**출력 형식** (JSON만):
{{
  "variants": ["변종1", "변종2", "변종3", "변종4", "변종5"]
}}"""
            
            # Gemini로 변종 생성
            result = self.classify_text(augment_prompt)
            
            if result['success']:
                try:
                    variants = result['classification'].get('variants', [])
                    
                    if variants and len(variants) > 0:
                        print(f"   ✅ 변종 생성 완료: {len(variants)}개")
                        for v in variants[:3]:
                            print(f"      - {v[:60]}...")
                        
                        # 변종 데이터를 새로운 행으로 DB 삽입 (선택적)
                        # 여기서는 로그만 출력하고, 실제 삽입은 주석 처리
                        # for variant in variants:
                        #     insert_url = f"{self.supabase_url}/rest/v1/phishing_news"
                        #     insert_data = {
                        #         'title': f"[증강] {variant[:100]}",
                        #         'content': variant,
                        #         'category': 'REAL_CASE',
                        #         'phishing_type': phishing_type,
                        #         'source': 'augmented',
                        #         'original_language': 'ko'
                        #     }
                        #     requests.post(insert_url, headers=self.headers, json=insert_data)
                        
                        augmented_count += len(variants)
                    else:
                        print(f"   ⚠️  변종 생성 실패 (빈 결과)")
                except Exception as e:
                    print(f"   ⚠️  변종 파싱 실패: {e}")
            else:
                print(f"   ❌ 변종 생성 실패")
            
            print()
            time.sleep(2)
        
        print(f"\n{'='*70}")
        print(f"📊 증강 완료")
        print(f"{'='*70}")
        print(f"   총 변종 생성: {augmented_count}개")
        print(f"   (실제 DB 삽입은 주석 처리됨 - 필요시 코드 수정)")
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
    
    classifier = DataClassifier(
        gemini_keys=gemini_keys if gemini_keys else [],
        openai_key=openai_key,
        supabase_url=supabase_url,
        supabase_key=supabase_key
    )
    
    print(f"\n{'='*70}")
    print(f"🎯 피싱 데이터 분류 시스템")
    print(f"{'='*70}")
    print(f"1️⃣  데이터 분류 (뉴스)")
    print(f"2️⃣  데이터 증강 (변종 생성) - 선택적")
    print(f"{'='*70}\n")
    
    # 1. 뉴스 데이터 분류 (전체)
    classifier.classify_news_data(limit=500)
    
    # 2. 데이터 증강 (선택적 - 주석 해제시 실행)
    # classifier.augment_phishing_data(limit=10)
    
    print("\n🎉 모든 작업 완료!")

if __name__ == "__main__":
    main()
