"""
URL 안전성 검사 (Google Safe Browsing API)
"""
import os
import requests
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

SAFE_BROWSING_API_KEY = os.getenv('GOOGLE_SAFE_BROWSING_API_KEY')

class URLChecker:
    def __init__(self):
        self.api_key = SAFE_BROWSING_API_KEY
        self.api_url = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
    
    def check_urls(self, urls: List[str]) -> List[Dict]:
        """
        URL 안전성 검사
        
        Returns:
            [{'url': str, 'is_safe': bool, 'threat_type': str, 'score': int}]
        """
        if not urls or not self.api_key:
            return []
        
        results = []
        
        try:
            payload = {
                "client": {
                    "clientId": "phishingapp",
                    "clientVersion": "1.0.0"
                },
                "threatInfo": {
                    "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
                    "platformTypes": ["ANY_PLATFORM"],
                    "threatEntryTypes": ["URL"],
                    "threatEntries": [{"url": url} for url in urls]
                }
            }
            
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            # 결과 파싱
            matches = data.get('matches', [])
            
            for url in urls:
                threat_match = next((m for m in matches if m['threat']['url'] == url), None)
                
                if threat_match:
                    threat_type = threat_match['threatType']
                    results.append({
                        'url': url,
                        'is_safe': False,
                        'threat_type': threat_type,
                        'score': 50  # 위험 URL 발견 시 +50점
                    })
                else:
                    results.append({
                        'url': url,
                        'is_safe': True,
                        'threat_type': None,
                        'score': 0
                    })
        
        except Exception as e:
            print(f"URL 검사 오류: {e}")
            # API 실패 시 기본값 반환
            for url in urls:
                results.append({
                    'url': url,
                    'is_safe': None,  # 알 수 없음
                    'threat_type': 'API_ERROR',
                    'score': 0
                })
        
        return results
