"""
LLM 기반 메시지 분석 (OpenAI GPT-4o-mini)
"""
import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict
import json

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


class LLMAnalyzer:
    """LLM 기반 피싱 분석 (OpenAI)"""
    
    def __init__(self):
        """초기화"""
        self.client = OpenAI(api_key=OPENAI_API_KEY)
    
    def analyze_message(self, message: str, retry: int = 2) -> Dict:
        """
        메시지를 LLM으로 분석
        
        Args:
            message: 분석할 메시지
            retry: 재시도 횟수
        
        Returns:
            {
                'is_phishing': bool,
                'confidence': float (0-1),
                'risk_score': int (0-100),
                'phishing_type': str,
                'reasoning': str,
                'red_flags': list
            }
        """
        
        system_prompt = """당신은 피싱/스미싱 탐지 전문가입니다. 메시지를 분석하여 피싱 여부를 판단하세요.

판단 기준:
1. 긴급성 강조 (즉시, 긴급, 24시간 내, 급한일, 빨리)
2. 금전 요구 또는 유도 (송금, 환급, 결제, 돈, 투자, 주식, 코인, 가상화폐)
3. 개인정보 요구 (카드번호, 비밀번호, 주민번호, 계좌)
4. 링크 클릭 유도
5. 공공기관/금융기관/택배회사 사칭
6. 협박/불안 조성
7. 파격적 혜택 제시 (높은 수익률, 무료, 당첨)
8. 가족/지인 사칭의 특징:
   - "엄마", "아빠", "팀장", "부장" 등 호칭 사용
   - 휴대폰 고장/번호 변경 주장
   - 긴급한 부탁이나 연락 요청
   - 돈/투자 관련 대화 유도 (간접적 금전 요구)
   - 정상적인 대화인 척하며 신뢰 구축 시도

**중요**: 
- 가족을 사칭하며 투자나 금전 관련 대화를 유도하는 경우 높은 위험도로 판단
- "의견을 묻는" 형식이라도 돈/투자 관련이면 의심
- 실제 가족이라면 다른 방법으로 연락 가능하므로, 의심스러운 상황 설정 자체가 피싱 신호

반드시 다음 JSON 형식으로만 응답하세요:
{
    "is_phishing": true/false,
    "confidence": 0.0-1.0,
    "risk_score": 0-100,
    "phishing_type": "기관사칭/택배사칭/가족사칭/투자사기/기타/정상",
    "reasoning": "판단 근거 (1-2문장)",
    "red_flags": ["의심 요소1", "의심 요소2"]
}"""

        user_prompt = f"""다음 메시지를 분석하세요:

\"\"\"{message}\"\"\""""

        for attempt in range(retry):
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.3,
                    max_tokens=500
                )
                
                # JSON 파싱
                text = response.choices[0].message.content.strip()
                result = json.loads(text)
                
                # 검증
                required_keys = ['is_phishing', 'confidence', 'risk_score', 'phishing_type', 'reasoning', 'red_flags']
                if all(key in result for key in required_keys):
                    print(f"🤖 LLM 분석 완료: {result['phishing_type']} (확신도: {result['confidence']:.2f})")
                    return result
                else:
                    raise ValueError("응답에 필수 키가 없습니다")
                
            except Exception as e:
                print(f"🤖 LLM 분석 오류 (시도 {attempt + 1}/{retry}): {e}")
                
                if attempt == retry - 1:
                    # 기본값 반환 (LLM 실패시)
                    return {
                        'is_phishing': False,
                        'confidence': 0.0,
                        'risk_score': 0,
                        'phishing_type': '분석실패',
                        'reasoning': f'LLM 분석 실패: {str(e)[:100]}',
                        'red_flags': []
                    }
        
        return None
