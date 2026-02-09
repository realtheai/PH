#!/usr/bin/env python3
import requests
import json

message = "엄마 나 폰고장나서 as맡겼어 꼭 좀 부탁할거있어 문자확인하는대로 답장줄수있어?"

print("\n" + "="*100)
print("🧪 가족사칭 피싱 테스트")
print("="*100)
print(f"\n메시지: {message}\n")

response = requests.post(
    "http://localhost:8888/api/v1/analyze",
    json={"message": message},
    timeout=30
)

if response.status_code == 200:
    result = response.json()
    
    print("📊 분석 결과:")
    print(f"   위험도 점수: {result['risk_score']}/100")
    print(f"   위험 수준: {result['risk_level']}")
    print(f"   피싱 여부: {'🔴 피싱' if result['is_phishing'] else '🟢 안전'}")
    print(f"   피싱 유형: {result.get('phishing_type', 'N/A')}")
    
    if result.get('similar_cases_count', 0) > 0:
        print(f"\n🔍 유사 피싱 사례: {result['similar_cases_count']}건 발견")
        print(f"   DB 유사도 점수: +{result.get('db_similarity_score', 0)}점")
    else:
        print(f"\n🔍 유사 피싱 사례: 없음")
    
    if result.get('llm_analysis'):
        llm = result['llm_analysis']
        print(f"\n🤖 AI 분석:")
        print(f"   판단: {llm.get('phishing_type', 'N/A')}")
        print(f"   확신도: {llm.get('confidence', 0):.2f}")
        print(f"   위험 점수: {llm.get('risk_score', 0)}")
        print(f"   근거: {llm.get('reasoning', 'N/A')}")
        if llm.get('red_flags'):
            print(f"   의심 요소: {', '.join(llm['red_flags'])}")
    
    print(f"\n💡 권장사항 (상위 3개):")
    for rec in result.get('recommendations', [])[:3]:
        print(f"   - {rec}")
    
else:
    print(f"❌ 분석 실패: {response.status_code}")
    print(f"   응답: {response.text}")

print("\n" + "="*100 + "\n")
