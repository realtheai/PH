"""
위험도 점수 계산 및 권장사항 생성
"""
from typing import List, Dict, Tuple

class Scorer:
    @staticmethod
    def calculate_risk_level(score: int) -> str:
        """
        위험도 수준 계산
        
        - 0-20: safe (안전)
        - 21-50: medium (주의)
        - 51-80: high (위험)
        - 81-100: critical (매우 위험)
        """
        if score <= 20:
            return 'safe'
        elif score <= 50:
            return 'medium'
        elif score <= 80:
            return 'high'
        else:
            return 'critical'
    
    @staticmethod
    def generate_recommendations(
        risk_level: str,
        matched_rules: List[Dict],
        url_results: List[Dict],
        phishing_type: str
    ) -> List[str]:
        """권장사항 생성"""
        recommendations = []
        
        # 위험도별 기본 권장사항
        if risk_level == 'safe':
            recommendations.append("✅ 현재 메시지는 안전한 것으로 판단됩니다.")
            recommendations.append("💡 그래도 의심스러운 부분이 있다면 발신자를 확인하세요.")
        
        elif risk_level == 'medium':
            recommendations.append("⚠️ 주의가 필요한 메시지입니다.")
            recommendations.append("📞 발신자가 정말 해당 기관인지 공식 번호로 직접 확인하세요.")
        
        elif risk_level == 'high':
            recommendations.append("🚨 위험한 메시지입니다. 즉시 대응을 중단하세요.")
            recommendations.append("❌ 링크 클릭, 송금, 개인정보 제공을 절대 하지 마세요.")
            recommendations.append("📞 의심되는 기관이 있다면 공식 번호로 직접 확인하세요.")
        
        elif risk_level == 'critical':
            recommendations.append("⛔ 매우 위험한 피싱 메시지입니다!")
            recommendations.append("❌ 어떠한 요구에도 응하지 마세요.")
            recommendations.append("🚔 112 또는 금융감독원(1332)에 즉시 신고하세요.")
        
        # 룰별 특화 권장사항
        categories = [rule['category'] for rule in matched_rules]
        
        if '기관사칭' in categories:
            recommendations.append("🏛️ 공공기관은 전화로 금전을 요구하지 않습니다.")
        
        if '금전요구' in categories:
            recommendations.append("💰 송금 전 반드시 가족이나 지인에게 확인하세요.")
        
        if '긴급성' in categories:
            recommendations.append("⏰ '즉시', '긴급' 등으로 심리적 압박을 가하는 건 전형적인 피싱 수법입니다.")
        
        # URL 관련
        unsafe_urls = [r for r in url_results if r.get('is_safe') == False]
        if unsafe_urls:
            recommendations.append("🔗 위험한 URL이 포함되어 있습니다. 절대 클릭하지 마세요.")
        
        # 피싱 유형별 특화 권장사항
        if phishing_type == '상품권사기':
            recommendations.append("🎁 상품권 요구는 100% 사기입니다.")
        elif phishing_type == '대출사기':
            recommendations.append("🏦 저금리/무담보 대출을 미끼로 수수료를 요구하면 대출사기입니다.")
            recommendations.append("📞 금융감독원(1332)에서 정식 등록 여부를 확인하세요.")
        elif phishing_type == '로맨스스캠':
            recommendations.append("💔 온라인에서 만난 상대가 금전을 요구하면 로맨스 스캠입니다.")
            recommendations.append("🚫 어떤 이유로든 해외 송금을 하지 마세요.")
        elif phishing_type == '채용사기':
            recommendations.append("💼 채용 과정에서 선입금을 요구하는 곳은 사기입니다.")
            recommendations.append("🔍 고용노동부 워크넷에서 해당 기업을 확인하세요.")
        elif phishing_type == '쇼핑사기':
            recommendations.append("🛒 비정상적으로 저렴한 가격은 사기 가능성이 높습니다.")
            recommendations.append("🔍 사업자등록번호와 통신판매신고번호를 확인하세요.")
        elif phishing_type == '계정탈취':
            recommendations.append("🔐 비밀번호 변경은 반드시 공식 앱/사이트에서 직접 하세요.")
            recommendations.append("🚫 문자/메일의 링크로 로그인하지 마세요.")
        elif phishing_type == '가족사칭':
            recommendations.append("👨‍👩‍👧 가족이 맞는지 반드시 기존 번호로 직접 전화해서 확인하세요.")

        return recommendations
