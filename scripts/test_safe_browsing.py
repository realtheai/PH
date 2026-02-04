"""
Google Safe Browsing API 테스트
"""
import os
import requests
from dotenv import load_dotenv

# .env 로드
load_dotenv()

API_KEY = os.getenv('GOOGLE_SAFE_BROWSING_API_KEY')

def check_url_safety(urls):
    """
    Google Safe Browsing API로 URL 안전성 체크
    
    Args:
        urls: 체크할 URL 리스트
        
    Returns:
        dict: URL별 위협 정보
    """
    endpoint = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={API_KEY}"
    
    payload = {
        "client": {
            "clientId": "phishingapp",
            "clientVersion": "1.0.0"
        },
        "threatInfo": {
            "threatTypes": [
                "MALWARE",
                "SOCIAL_ENGINEERING",
                "UNWANTED_SOFTWARE",
                "POTENTIALLY_HARMFUL_APPLICATION"
            ],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url} for url in urls]
        }
    }
    
    try:
        response = requests.post(endpoint, json=payload, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API 요청 실패: {e}")
        return None

def main():
    print("="*60)
    print("🔍 Google Safe Browsing API 테스트")
    print("="*60)
    
    # 테스트 URL 목록
    test_urls = [
        "http://testsafebrowsing.appspot.com/s/phishing.html",  # 구글 테스트용 피싱 URL
        "http://testsafebrowsing.appspot.com/s/malware.html",   # 구글 테스트용 악성코드 URL
        "https://www.google.com",                                # 안전한 URL
        "https://www.naver.com",                                 # 안전한 URL
    ]
    
    print(f"\n📋 테스트 URL: {len(test_urls)}개")
    for url in test_urls:
        print(f"   - {url}")
    
    print(f"\n🔑 API Key: {API_KEY[:20]}...")
    print(f"\n⏳ API 호출 중...\n")
    
    result = check_url_safety(test_urls)
    
    if result:
        if 'matches' in result and result['matches']:
            print("⚠️  위협 발견!\n")
            for match in result['matches']:
                print(f"🚨 위험 URL: {match['threat']['url']}")
                print(f"   위협 유형: {match['threatType']}")
                print(f"   플랫폼: {match['platformType']}")
                print(f"   위협 항목: {match['threatEntryType']}")
                print()
        else:
            print("✅ 모든 URL이 안전합니다!")
        
        print("\n" + "="*60)
        print("✅ API 테스트 성공!")
        print("="*60)
        
        # 응답 전체 출력 (디버깅용)
        print("\n📄 전체 응답:")
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    else:
        print("\n" + "="*60)
        print("❌ API 테스트 실패!")
        print("="*60)

if __name__ == "__main__":
    main()
