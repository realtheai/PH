#!/usr/bin/env python3
import requests
import json

message = "엄마, 나 주식으로 돈 좀 벌어볼까 하는데 어때? 요즘 주식하는 사람들도 많고 수익률도 괜찮다고 하던데"

print("\n" + "="*100)
print("🧪 가족사칭 + 투자사기 피싱 테스트")
print("="*100)
print(f"\n메시지: {message}\n")

try:
    response = requests.post(
        "http://localhost:8888/api/v1/analyze",
        json={"message": message},
        timeout=30
    )
    
    print(f"HTTP 상태: {response.status_code}\n")
    
    if response.status_code == 200:
        result = response.json()
        
        print("="*100)
        print("📊 최종 분석 결과")
        print("="*100)
        print(f"   위험도 점수: {result['risk_score']}/100")
        print(f"   위험 수준: {result['risk_level']}")
        print(f"   피싱 여부: {'🔴 피싱' if result['is_phishing'] else '🟢 안전'}")
        print(f"   피싱 유형: {result.get('phishing_type', 'N/A')}")
        
        print("\n" + "="*100)
        print("🔍 벡터 검색 결과")
        print("="*100)
        if result.get('similar_cases_count', 0) > 0:
            print(f"   유사 사례: {result['similar_cases_count']}건 발견")
            print(f"   DB 유사도 점수: +{result.get('db_similarity_score', 0)}점")
        else:
            print(f"   유사 사례: 발견 안됨")
        
        print("\n" + "="*100)
        print("🤖 LLM 분석 상세")
        print("="*100)
        if result.get('llm_analysis'):
            llm = result['llm_analysis']
            print(f"   is_phishing: {llm.get('is_phishing', False)}")
            print(f"   판단: {llm.get('phishing_type', 'N/A')}")
            print(f"   확신도: {llm.get('confidence', 0):.2f}")
            print(f"   위험 점수: {llm.get('risk_score', 0)}")
            print(f"   근거: {llm.get('reasoning', 'N/A')}")
            if llm.get('red_flags'):
                print(f"   의심 요소: {', '.join(llm['red_flags'])}")
        else:
            print("   LLM 분석 없음")
        
        print("\n" + "="*100)
        print("📋 매칭된 룰")
        print("="*100)
        if result.get('matched_rules'):
            for rule in result['matched_rules']:
                print(f"   - {rule.get('category')}: {rule.get('matched_keyword')} (+{rule.get('score')}점)")
        else:
            print("   매칭된 룰 없음")
        
    else:
        print(f"❌ 분석 실패")
        print(f"   응답: {response.text}")
        
except Exception as e:
    print(f"❌ 오류 발생: {e}")

print("\n" + "="*100 + "\n")
