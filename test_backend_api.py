#!/usr/bin/env python3
"""
백엔드 API 벡터 검색 테스트
"""
import requests
import json

API_URL = "http://localhost:8888"

# 테스트 메시지들
test_messages = [
    {
        "name": "택배 피싱",
        "message": "[Web발신] CJ대한통운 고객님 소포 반송 처리되었습니다. 주소지 다시 확인해주세요. http://bit.ly/xxxxx"
    },
    {
        "name": "금융기관 사칭",
        "message": "국민은행입니다. 보안등급 강화를 위해 즉시 본인인증이 필요합니다. 링크 접속: http://kb-safe.com"
    },
    {
        "name": "가족 사칭",
        "message": "엄마 휴대폰 고장났어. 급한일 있어서 이 번호로 연락해. 010-1234-5678"
    },
    {
        "name": "정상 메시지",
        "message": "내일 저녁 7시에 강남역에서 만나요. 약속 잊지마세요!"
    }
]

print("\n" + "="*100)
print("🧪 피싱 분석 API 테스트 (벡터 검색 포함)")
print("="*100 + "\n")

# 백엔드 헬스 체크
try:
    health = requests.get(f"{API_URL}/health", timeout=5)
    if health.status_code == 200:
        print("✅ 백엔드 연결 성공\n")
    else:
        print(f"❌ 백엔드 응답 오류: {health.status_code}\n")
        exit(1)
except Exception as e:
    print(f"❌ 백엔드 연결 실패: {e}\n")
    exit(1)

# 각 메시지 테스트
for idx, test in enumerate(test_messages, 1):
    print(f"{'='*100}")
    print(f"테스트 {idx}: {test['name']}")
    print(f"{'='*100}")
    print(f"메시지: {test['message']}\n")
    
    try:
        response = requests.post(
            f"{API_URL}/api/v1/analyze",
            json={"message": test['message']},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"📊 분석 결과:")
            print(f"   위험도 점수: {result['risk_score']}/100")
            print(f"   위험 수준: {result['risk_level']}")
            print(f"   피싱 여부: {'🔴 피싱' if result['is_phishing'] else '🟢 안전'}")
            
            if result.get('phishing_type'):
                print(f"   피싱 유형: {result['phishing_type']}")
            
            # 유사 사례 정보
            if result.get('similar_cases_count', 0) > 0:
                print(f"\n🔍 유사 피싱 사례: {result['similar_cases_count']}건 발견")
                print(f"   DB 유사도 점수: +{result.get('db_similarity_score', 0)}점")
            else:
                print(f"\n🔍 유사 피싱 사례: 없음")
            
            # LLM 분석
            if result.get('llm_analysis'):
                llm = result['llm_analysis']
                print(f"\n🤖 AI 분석:")
                print(f"   판단: {llm.get('phishing_type', 'N/A')}")
                print(f"   확신도: {llm.get('confidence', 0):.2f}")
                print(f"   근거: {llm.get('reasoning', 'N/A')}")
            
            # 권장사항 (첫 3개만)
            if result.get('recommendations'):
                print(f"\n💡 권장사항:")
                for rec in result['recommendations'][:3]:
                    print(f"   - {rec}")
            
            print()
            
        else:
            print(f"❌ 분석 실패: {response.status_code}")
            print(f"   응답: {response.text}\n")
            
    except Exception as e:
        print(f"❌ 오류: {e}\n")
    
    print()

print("="*100)
print("✅ 테스트 완료!")
print("="*100 + "\n")
