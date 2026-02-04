"""
Request/Response Pydantic 모델
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AnalyzeRequest(BaseModel):
    """메시지 분석 요청"""
    message: str
    urls: Optional[List[str]] = []

class RiskDetail(BaseModel):
    """위험 상세 정보"""
    category: str           # '기관사칭', '긴급성', '금전요구' 등
    matched_keyword: str    # 매칭된 키워드
    score: int              # 해당 항목 점수
    description: str        # 설명

class AnalyzeResponse(BaseModel):
    """메시지 분석 결과"""
    risk_score: int                      # 위험도 점수 (0-100)
    risk_level: str                      # 위험 수준 ('safe', 'medium', 'high', 'critical')
    is_phishing: bool                    # 피싱 여부
    phishing_type: Optional[str]         # 피싱 유형
    matched_rules: List[RiskDetail]      # 매칭된 룰
    url_check_results: List[dict]        # URL 검사 결과
    recommendations: List[str]           # 권장사항
    analyzed_at: datetime                # 분석 시간

class StatsResponse(BaseModel):
    """통계 응답"""
    total_news: int
    total_images: int
    recent_phishing_types: List[dict]
    daily_stats: List[dict]
