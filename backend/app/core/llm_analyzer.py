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
    
    def analyze_message(self, message: str, similar_cases: list = None, retry: int = 2) -> Dict:
        """
        메시지를 LLM으로 분석

        Args:
            message: 분석할 메시지
            similar_cases: 벡터 검색으로 찾은 유사 피싱 사례 리스트
            retry: 재시도 횟수

        Returns:
            {
                'is_phishing': bool,
                'confidence': float (0-1),
                'risk_score': int (0-100),
                'phishing_type': str,
                'reasoning': str,
                'red_flags': list,
                'db_relevance': bool
            }
        """
        
        system_prompt = """당신은 피싱/스미싱 탐지 전문가입니다. 메시지를 분석하여 피싱 여부를 판단하세요.

**판단 기준:**
1. 긴급성 강조 (즉시, 긴급, 24시간 내, 급한일, 빨리)
2. 금전 요구 또는 유도 (송금, 환급, 결제, 돈, 투자, 주식, 코인, 가상화폐)
3. 개인정보 요구 (카드번호, 비밀번호, 주민번호, 계좌)
4. 링크 클릭 유도
5. 공공기관/금융기관/택배회사 사칭
6. 협박/불안 조성
7. 파격적 혜택 제시 (높은 수익률, 무료, 당첨)
8. 가족/지인 사칭:
   - "엄마", "아빠", "팀장", "부장" 등 호칭 사용
   - 휴대폰 고장/번호 변경 주장
   - 긴급한 부탁이나 연락 요청
   - 돈/투자 관련 대화 유도 (간접적 금전 요구)
   - 정상적인 대화인 척하며 신뢰 구축 시도
9. 대출 사기: 저금리/무담보 대출 유도, 수수료 선입금 요구
10. 로맨스 스캠: 연애감정 이용, 해외 송금 요구
11. 채용/알바 사기: 고수익 재택근무, 선입금 요구
12. 쇼핑 사기: 가짜 쇼핑몰, 비정상 결제 유도
13. 계정탈취: 비밀번호 변경/로그인 확인 유도, 가짜 인증 페이지

**중요 - 오탐 방지:**
- "카카오톡으로 사진 보내줘", "택배 잘 받았어", "네이버에서 검색해봐" 같은 일상 대화는 정상입니다
- 단순히 기업명/서비스명이 언급된다고 피싱이 아닙니다
- ㅋㅋ, ㅎㅎ, ㅠㅠ 등 이모티콘, "고마워", "밥 먹었어?" 같은 일상 표현이 있으면 정상일 가능성이 높습니다
- 피싱 판단은 "개인정보 요구/계좌이체 요구/악성앱 설치 유도"가 있을 때만 하세요

**중요 - 합법 메시지 구별 (정상으로 판단해야 함):**
- "광고)" 또는 "(광고)": 한국 법률상 의무 표기. 합법 광고 메시지입니다
- "무료 거부 080-XXX-XXXX": 법적 의무 수신거부 번호. 합법 마케팅입니다
- "[Web발신]": 통신사가 표시하는 합법 발신 표시입니다
- 운송장번호, 배송 완료, 고객센터 번호(1588-/1577-/1544-): 정상 택배/기업 알림입니다
- 패스트캠퍼스, 인프런, 클래스101 등 교육 플랫폼 광고: 합법 마케팅입니다
- 할인 쿠폰, 이벤트 안내: 수신거부 번호가 있으면 합법 광고입니다
- 피싱과 광고의 핵심 차이: 광고는 "상품 구매"를 유도하고, 피싱은 "개인정보/계좌이체/앱설치"를 요구합니다

**중요 - 무단 결제 알림 스미싱 (높은 위험도):**
- 쇼핑몰 결제 완료/승인 알림 형식이지만, 실제로는 스미싱입니다
- 특징:
  * 사용자가 주문하지 않은 결제 알림으로 불안 조성
  * 큰 금액 언급 (30만원 이상)으로 즉각 반응 유도
  * 문의 전화번호가 일반 전화번호 (02-XXXX-XXXX, 031-XXX-XXXX 등)
  * 정상 쇼핑몰은 1588/1577/1544 같은 대표번호 사용
  * 링크가 없어도 전화를 유도하는 방식
- 판단 기준: "결제완료/주문완료/결제승인" + "금액" + "일반 전화번호" 조합 → 높은 피싱 가능성
- 예외: 실제 주문 내역, 상품명, 배송지 등 구체적 정보가 있으면 정상일 수 있음

**중요 - 가족 사칭:**
- 가족을 사칭하며 투자나 금전 관련 대화를 유도하는 경우 높은 위험도로 판단
- "의견을 묻는" 형식이라도 돈/투자 관련이면 의심
- 실제 가족이라면 다른 방법으로 연락 가능하므로, 의심스러운 상황 설정 자체가 피싱 신호

**중요 - DB 유사 사례 활용:**
- DB에서 유사한 피싱 사례가 제공될 수 있습니다
- 유사 사례는 참고용이며, 반드시 분석 대상 메시지의 실제 내용과 의도를 기준으로 판단하세요
- 정상 택배 알림이 "택배 사칭 피싱"과 표면적으로 유사할 수 있지만, 개인정보 요구/앱 설치 유도가 없으면 정상입니다
- 합법 광고가 "투자 사기"와 단어가 겹칠 수 있지만, 수신거부 번호가 있고 상품 구매만 유도하면 정상입니다
- db_relevance: 유사 사례가 실제로 분석 메시지의 판단에 관련이 있으면 true, 표면적 유사일 뿐이면 false

반드시 다음 JSON 형식으로만 응답하세요:
{
    "is_phishing": true/false,
    "confidence": 0.0-1.0,
    "risk_score": 0-100,
    "phishing_type": "기관사칭/택배사칭/가족사칭/투자사기/대출사기/로맨스스캠/채용사기/쇼핑사기/계정탈취/기타/정상",
    "reasoning": "판단 근거 (1-2문장, 한국어)",
    "red_flags": ["의심 요소1", "의심 요소2"],
    "db_relevance": true/false
}"""

        # 유사 사례 컨텍스트 구성
        similar_context = ""
        if similar_cases:
            similar_context = "\n\n**[참고] DB에서 발견된 유사 피싱 사례:**\n"
            for i, case in enumerate(similar_cases[:3], 1):
                title = (case.get('title') or '제목 없음')[:80]  # None 체크 추가
                content_snippet = (case.get('content') or '')[:100]  # None 체크 추가
                p_type = case.get('phishing_type') or '미분류'  # None 체크 추가
                similarity = case.get('similarity', 0)
                similar_context += f"{i}. [{p_type}] {title} (유사도: {similarity:.0%})\n"
                if content_snippet:
                    similar_context += f"   내용: {content_snippet}...\n"
            similar_context += "\n위 유사 사례는 참고용입니다. 유사 사례가 있더라도 분석 대상 메시지의 실제 내용을 기준으로 판단하세요.\n정상적인 택배 알림, 합법 광고 등이 피싱 사례와 표면적으로 유사할 수 있지만, 실제 의도가 다르면 정상으로 판단해야 합니다."

        user_prompt = f"""다음 메시지를 분석하세요:

\"\"\"{message}\"\"\"{similar_context}"""

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
                    # db_relevance 기본값 설정 (LLM이 누락할 경우 대비)
                    if 'db_relevance' not in result:
                        result['db_relevance'] = False
                    print(f"🤖 LLM 분석 완료: {result['phishing_type']} (확신도: {result['confidence']:.2f}, DB관련: {result['db_relevance']})")
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
