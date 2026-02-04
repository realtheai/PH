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
from app.core.embedder import Embedder
from app.core.llm_analyzer import LLMAnalyzer
import os
import requests

router = APIRouter()

# 엔진 초기화
rule_engine = RuleEngine()
url_checker = URLChecker()
scorer = Scorer()
embedder = Embedder()
llm_analyzer = LLMAnalyzer()

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
        
        # 9. Vector Search - DB에서 유사한 피싱 사례 찾기
        similar_cases = []
        db_similarity_score = 0
        
        try:
            print(f"🔍 Vector Search 시작: {message[:50]}...")
            
            # 임베딩 생성
            query_embedding = embedder.create_embedding(message)
            print(f"✅ 임베딩 생성 완료 (차원: {len(query_embedding) if query_embedding else 0})")
            
            if not query_embedding:
                raise Exception("임베딩 생성 실패")
            
            # Supabase에서 유사도 검색 (REST API 직접 호출)
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_ANON_KEY')
            
            headers = {
                'apikey': supabase_key,
                'Authorization': f'Bearer {supabase_key}',
                'Content-Type': 'application/json'
            }
            
            rpc_url = f"{supabase_url}/rest/v1/rpc/find_similar_phishing"
            payload = {
                'query_embedding': query_embedding,
                'match_threshold': 0.5,  # 0.7 -> 0.5로 낮춤
                'match_count': 3
            }
            
            print(f"🌐 RPC 호출: {rpc_url}")
            response = requests.post(rpc_url, headers=headers, json=payload, timeout=10)
            print(f"📡 응답 코드: {response.status_code}")
            response.raise_for_status()
            
            result_data = response.json()
            print(f"📊 결과: {len(result_data) if result_data else 0}건")
            
            if result_data:
                similar_cases = result_data
                # 가장 유사한 사례의 유사도를 점수에 반영
                if similar_cases:
                    max_similarity = similar_cases[0].get('similarity', 0)
                    db_similarity_score = int(max_similarity * 50)  # 최대 50점 추가
                    
                    # 유사 사례가 있으면 총 점수에 반영
                    total_score = min(total_score + db_similarity_score, 100)
                    
                    # 위험도 재계산
                    risk_level = scorer.calculate_risk_level(total_score)
                    is_phishing = total_score > 50
                    
                    print(f"✅ 유사 사례 {len(similar_cases)}건 발견 (최대 유사도: {max_similarity:.2f})")
        except Exception as e:
            print(f"⚠️  Vector Search 실패: {e}")
            import traceback
            traceback.print_exc()
            # Vector Search 실패해도 Rule-based는 계속 작동
        
        # 10. LLM 분석 (GPT-4o-mini로 메시지 직접 분석)
        llm_result = None
        try:
            print(f"🤖 LLM 분석 시작...")
            llm_result = llm_analyzer.analyze_message(message)
            
            if llm_result and llm_result.get('is_phishing'):
                llm_score = llm_result.get('risk_score', 0)
                llm_confidence = llm_result.get('confidence', 0)
                
                # LLM 점수 반영 (확신도 높으면 더 많이 반영)
                llm_weighted_score = int(llm_score * llm_confidence)
                
                # 기존 점수와 LLM 점수를 조합 (LLM 우선순위 높음)
                total_score = int(total_score * 0.4 + llm_weighted_score * 0.6)
                total_score = min(total_score, 100)
                
                # 위험도 재계산
                risk_level = scorer.calculate_risk_level(total_score)
                is_phishing = total_score > 50
                
                # 피싱 유형 업데이트 (LLM이 더 정확)
                if llm_result.get('phishing_type') != '정상':
                    phishing_type = llm_result.get('phishing_type')
                
                print(f"✅ LLM 분석 완료: {phishing_type} (확신도: {llm_confidence:.2f}, 점수: {llm_score})")
        except Exception as e:
            print(f"⚠️  LLM 분석 실패: {e}")
            # LLM 실패해도 계속 진행
        
        # 11. 권장사항 생성
        recommendations = scorer.generate_recommendations(
            risk_level, matched_rules, url_check_results, phishing_type
        )
        
        # 유사 사례 정보 추가
        if similar_cases:
            recommendations.insert(0, 
                f"📊 DB에서 유사한 피싱 사례 {len(similar_cases)}건이 발견되었습니다."
            )
        
        # LLM 분석 결과 추가
        if llm_result and llm_result.get('reasoning'):
            recommendations.insert(0, f"🤖 AI 분석: {llm_result['reasoning']}")
        
        # 12. 응답 생성
        return AnalyzeResponse(
            risk_score=total_score,
            risk_level=risk_level,
            is_phishing=is_phishing,
            phishing_type=phishing_type,
            matched_rules=[RiskDetail(**rule) for rule in matched_rules],
            url_check_results=url_check_results,
            recommendations=recommendations,
            analyzed_at=datetime.now(),
            similar_cases_count=len(similar_cases) if similar_cases else 0,
            db_similarity_score=db_similarity_score,
            llm_analysis=llm_result
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 실패: {str(e)}")
