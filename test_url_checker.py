#!/usr/bin/env python3
"""
URL 검사 기능 테스트
"""
import requests

# 악성 URL과 정상 URL이 포함된 메시지 테스트
test_messages = [
    {
        "name": "악성 URL 포함",
        "message": "긴급! 계정 확인이 필요합니다. http://testsafebrowsing.appspot.com/s/malware.html 클릭하세요"
    },
    {
        "name": "의심 링크 (bit.ly)",
        "message": "[Web발신] 택배가 반송되었습니다. 주소 확인: http://bit.ly/3xxxxx"
    },
    {
        "name": "정상 URL",
        "message": "회의 자료입니다. https://docs.google.com/document/d/xxxxx"
    },
    {
        "name": "URL 없음",
        "message": "엄마 나 폰고장나서 as맡겼어 급한일 있어"
    }
]

print("\n" + "="*100)
print("🔍 URL 검사 기능 테스트")
print("="*100 + "\n")

for idx, test in enumerate(test_messages, 1):
    print(f"{'='*100}")
    print(f"[테스트 {idx}] {test['name']}")
    print(f"{'='*100}")
    print(f"메시지: {test['message']}\n")
    
    try:
        response = requests.post(
            "http://localhost:8888/api/v1/analyze",
            json={"message": test['message']},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"📊 분석 결과:")
            print(f"   위험도 점수: {result['risk_score']}/100")
            print(f"   피싱 여부: {'🔴 피싱' if result['is_phishing'] else '🟢 안전'}")
            
            # URL 검사 결과
            print(f"\n🔗 URL 검사 결과:")
            if result.get('url_check_results'):
                for url_result in result['url_check_results']:
                    status = '🔴 위험' if not url_result['is_safe'] else '✅ 안전'
                    print(f"   {status} {url_result['url']}")
                    if url_result.get('threat_type') and url_result['threat_type'] != 'API_ERROR':
                        print(f"      위협 유형: {url_result['threat_type']}")
                        print(f"      추가 점수: +{url_result['score']}점")
            else:
                print(f"   URL 없음")
            
            print()
            
        else:
            print(f"❌ 분석 실패: {response.status_code}\n")
            
    except Exception as e:
        print(f"❌ 오류: {e}\n")

print("="*100 + "\n")
