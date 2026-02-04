"""
메시지 분석 API 엔드포인트
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
import re
from typing import List

from app.schemas.request import AnalyzeRequest, AnalyzeResponse, RiskDetail
from app.core.rule_engine import RuleEngine
from app.core.url_checker import URLChecker
from app.core.scorer import Scorer

router = APIRouter()

# 엔진 초기화
rule_engine = RuleEngine()
url_checker = URLChecker()
scorer = Scorer()

def extract_urls(text: str) -> List[str]:
    """텍스트에서 URL 추출"""
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.findall(url_pattern, text)

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_message(request: AnalyzeRequest):
    """
    메시지 분석 엔드포인트
    
    - 룰 기반 검사
    - URL 안전성 검사
    - 위험도 점수 계산
    """
    try:
        message = request.message
        
        # 1. URL 추출
        extracted_urls = extract_urls(message)
        all_urls = list(set(extracted_urls + request.urls))  # 중복 제거
        
        # 2. 룰 기반 검사
        rule_score, matched_rules = rule_engine.check_message(message)
        
        # 3. URL 패턴 검사 (단축 URL 등)
        url_pattern_score, url_pattern_matches = rule_engine.check_urls(all_urls)
        matched_rules.extend(url_pattern_matches)
        
        # 4. URL 안전성 검사 (Google Safe Browsing)
        url_check_results = url_checker.check_urls(all_urls)
        url_safety_score = sum(r['score'] for r in url_check_results)
        
        # 5. 총 점수 계산
        total_score = min(rule_score + url_pattern_score + url_safety_score, 100)
        
        # 6. 위험도 수준
        risk_level = scorer.calculate_risk_level(total_score)
        
        # 7. 피싱 여부
        is_phishing = total_score > 50
        
        # 8. 피싱 유형 감지
        phishing_type = rule_engine.detect_phishing_type(message, matched_rules) if is_phishing else None
        
        # 9. 권장사항 생성
        recommendations = scorer.generate_recommendations(
            risk_level, matched_rules, url_check_results, phishing_type
        )
        
        # 10. 응답 생성
        return AnalyzeResponse(
            risk_score=total_score,
            risk_level=risk_level,
            is_phishing=is_phishing,
            phishing_type=phishing_type,
            matched_rules=[RiskDetail(**rule) for rule in matched_rules],
            url_check_results=url_check_results,
            recommendations=recommendations,
            analyzed_at=datetime.now()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 실패: {str(e)}")
