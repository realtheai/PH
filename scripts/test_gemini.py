"""
Gemini API 테스트 및 번역 기능 (REST API 직접 호출)
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

def test_gemini():
    """Gemini API 테스트"""
    print("="*60)
    print("🤖 Gemini API 테스트")
    print("="*60)
    
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY가 .env에 없습니다!")
        return False
    
    print(f"\n🔑 API Key: {GEMINI_API_KEY[:20]}...")
    
    try:
        print("\n⏳ 번역 테스트 중...")
        
        test_text = """
        This is a phishing scam targeting bank customers.
        The scammers impersonate officials and demand immediate payment.
        """
        
        prompt = f"""다음 영어 텍스트를 한국어로 자연스럽게 번역해주세요:

{test_text}

번역:"""
        
        # Gemini API 엔드포인트 (gemini-2.5-flash)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }
        
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        result_data = response.json()
        result = result_data['candidates'][0]['content']['parts'][0]['text']
        
        print("\n📄 원문:")
        print(test_text.strip())
        print("\n🇰🇷 번역 결과:")
        print(result.strip())
        
        print("\n" + "="*60)
        print("✅ Gemini API 테스트 성공!")
        print("="*60)
        
        return True
        
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ HTTP 오류: {e}")
        print(f"   응답: {e.response.text if e.response else 'None'}")
        return False
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        return False

if __name__ == "__main__":
    test_gemini()
