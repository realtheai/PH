"""
메시지 분석 API 엔드포인트
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone, timedelta
import re
from typing import List

from app.schemas.request import AnalyzeRequest, AnalyzeResponse, RiskDetail
from app.core.rule_engine import RuleEngine
from app.core.url_checker import URLChecker
from app.core.scorer import Scorer
from app.core.embedder import Embedder
from app.core.llm_analyzer import LLMAnalyzer
from app.core.vector_searcher import VectorSearcher
import os

router = APIRouter()

# 엔진 초기화
rule_engine = RuleEngine()
url_checker = URLChecker()
scorer = Scorer()
embedder = Embedder()
llm_analyzer = LLMAnalyzer()
vector_searcher = VectorSearcher()

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
            
            # pgvector RPC 방식 (전체 DB 검색, HNSW 인덱스)
            similar_cases = vector_searcher.search_similar_cases(
                query_embedding=query_embedding,
                threshold=0.3,  # 유사도 임계값 30% (0.3)
                limit=5  # 상위 5개 (뉴스 3개 + 이미지 2개)
            )
            
            print(f"📊 결과: {len(similar_cases)}건 발견")
            
            if similar_cases:
                max_similarity = similar_cases[0].get('similarity', 0)
                print(f"✅ 유사 사례 {len(similar_cases)}건 발견 (최대 유사도: {max_similarity:.2f})")
                # DB 유사도 점수는 LLM이 판단하므로 여기서는 가산하지 않음
                
        except Exception as e:
            print(f"⚠️  Vector Search 실패: {e}")
            import traceback
            traceback.print_exc()
            # Vector Search 실패해도 Rule-based는 계속 작동
        
        # 10. LLM 분석 (GPT-4o-mini로 메시지 직접 분석)
        llm_result = None
        try:
            print(f"🤖 LLM 분석 시작... (유사 사례 {len(similar_cases)}건 포함)")
            llm_result = llm_analyzer.analyze_message(message, similar_cases=similar_cases)
            
            if llm_result:
                llm_score = llm_result.get('risk_score', 0)
                llm_confidence = llm_result.get('confidence', 0)

                if llm_result.get('is_phishing'):
                    # LLM이 피싱으로 판단한 경우: 확신도 기반 가중 반영
                    if llm_confidence >= 0.8:
                        total_score = int(total_score * 0.2 + llm_score * 0.8)
                    elif llm_confidence >= 0.6:
                        total_score = int(total_score * 0.4 + llm_score * 0.6)
                    else:
                        llm_weighted_score = int(llm_score * llm_confidence)
                        total_score = int(total_score * 0.6 + llm_weighted_score * 0.4)

                    total_score = min(total_score, 100)

                    # 피싱 유형 업데이트 (LLM이 더 정확)
                    if llm_result.get('phishing_type') != '정상':
                        phishing_type = llm_result.get('phishing_type')

                    # LLM이 DB 유사 사례가 관련 있다고 판단한 경우 추가 가산
                    if similar_cases and llm_result.get('db_relevance'):
                        max_similarity = similar_cases[0].get('similarity', 0)
                        db_similarity_score = int(max_similarity * 20)  # 최대 20점
                        total_score = min(total_score + db_similarity_score, 100)
                        print(f"📊 DB 유사 사례 관련성 확인 → +{db_similarity_score}점")

                    print(f"✅ LLM 피싱 판정: {phishing_type} (확신도: {llm_confidence:.2f}, 점수: {llm_score})")
                else:
                    # LLM이 정상으로 판단한 경우: 룰 기반 오탐 보정
                    # LLM은 문맥을 이해하므로, 정상 판정 시 적극적으로 점수 낮춤
                    if llm_confidence >= 0.8:
                        total_score = int(total_score * 0.15)
                        print(f"✅ LLM 정상 판정 (확신도 높음): 점수 85% 감소 → {total_score}")
                    elif llm_confidence >= 0.5:
                        total_score = int(total_score * 0.3)
                        print(f"✅ LLM 정상 판정 (확신도 중간): 점수 70% 감소 → {total_score}")
                    else:
                        total_score = int(total_score * 0.5)
                        print(f"✅ LLM 정상 판정 (확신도 낮음): 점수 50% 감소 → {total_score}")

                # 위험도 재계산
                risk_level = scorer.calculate_risk_level(total_score)
                is_phishing = total_score > 50
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
        # KST (UTC+9) 시간대 설정
        KST = timezone(timedelta(hours=9))
        
        return AnalyzeResponse(
            risk_score=total_score,
            risk_level=risk_level,
            is_phishing=is_phishing,
            phishing_type=phishing_type,
            matched_rules=[RiskDetail(**rule) for rule in matched_rules],
            url_check_results=url_check_results,
            recommendations=recommendations,
            analyzed_at=datetime.now(KST),
            similar_cases_count=len(similar_cases) if similar_cases else 0,
            db_similarity_score=db_similarity_score,
            llm_analysis=llm_result
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 실패: {str(e)}")
