#!/usr/bin/env python3
"""
OpenAI 임베딩 전환 후 테스트
"""
import requests
import json

# 백엔드 URL (포트 9000)
BASE_URL = "http://localhost:9000"

def test_analyze(message: str):
    """메시지 분석 테스트"""
    print(f"\n{'='*80}")
    print(f"테스트 메시지: {message}")
    print(f"{'='*80}\n")
    
    response = requests.post(
        f"{BASE_URL}/api/v1/analyze",
        json={"message": message},
        timeout=30
    )
    
    if response.status_code != 200:
        print(f"❌ 오류: {response.status_code}")
        print(response.text)
        return
    
    result = response.json()
    
    print(f"🎯 최종 결과: {result['result']}")
    print(f"📊 위험도: {result['risk_score']}/100")
    print()
    
    # LLM 분석
    if result.get('llm_analysis'):
        llm = result['llm_analysis']
        print(f"🤖 LLM 분석:")
        print(f"   - 위험도: {llm['risk_score']}/100")
        print(f"   - 신뢰도: {llm['confidence']*100:.0f}%")
        print(f"   - 이유: {llm['reasoning'][:100]}...")
    
    # 벡터 검색
    if result.get('similar_cases'):
        print(f"\n🔍 유사 케이스: {len(result['similar_cases'])}개")
        for i, case in enumerate(result['similar_cases'][:3], 1):
            print(f"   {i}. [{case['phishing_type']}] {case['title'][:50]}... (유사도: {case['similarity']:.2f})")
    else:
        print("\n❌ 벡터 검색 실패!")
    
    print()

if __name__ == '__main__':
    print("\n" + "="*80)
    print("OpenAI 임베딩 전환 후 테스트")
    print("="*80)
    
    # 테스트 메시지들
    test_cases = [
        "엄마, 나 주식으로 돈 좀 벌어볼까 하는데 어때?",
        "국세청입니다. 미납 세금이 있어 환급 받으실 수 있습니다. https://bit.ly/abc123",
        "안녕하세요, 내일 회의 일정 확인 부탁드립니다."
    ]
    
    for message in test_cases:
        test_analyze(message)
        print()
