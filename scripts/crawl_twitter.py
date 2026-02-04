"""
X (Twitter) 피싱 경고 트윗 크롤러
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from typing import List, Dict
import time
import re

class TwitterPhishingCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def search_twitter(self, query: str, max_results: int = 50) -> List[Dict]:
        """트위터 검색 (Nitter 사용)"""
        results = []
        
        print(f"\n🔍 X (Twitter) 검색: '{query}'")
        
        try:
            # Nitter (Twitter alternative frontend) 사용
            nitter_instances = [
                'https://nitter.net',
                'https://nitter.poast.org',
                'https://nitter.privacydev.net'
            ]
            
            for instance in nitter_instances:
                try:
                    url = f"{instance}/search"
                    params = {
                        'f': 'tweets',
                        'q': query,
                        'since': '',
                        'until': '',
                        'near': ''
                    }
                    
                    response = self.session.get(url, params=params, timeout=10)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    tweets = soup.select('.timeline-item')
                    
                    for tweet in tweets[:max_results]:
                        try:
                            # 트윗 내용
                            content_elem = tweet.select_one('.tweet-content')
                            content = content_elem.get_text(strip=True) if content_elem else ''
                            
                            # 작성자
                            author_elem = tweet.select_one('.username')
                            author = author_elem.get_text(strip=True) if author_elem else ''
                            
                            # 링크
                            link_elem = tweet.select_one('.tweet-link')
                            tweet_url = instance + link_elem.get('href', '') if link_elem else ''
                            
                            # 날짜
                            date_elem = tweet.select_one('.tweet-date a')
                            date = date_elem.get('title', '') if date_elem else ''
                            
                            if content and self._is_phishing_related(content):
                                result = {
                                    'source': 'twitter',
                                    'query': query,
                                    'content': content,
                                    'author': author,
                                    'url': tweet_url,
                                    'date': date,
                                    'extracted_keywords': self._extract_keywords(content),
                                    'crawled_at': datetime.now().isoformat()
                                }
                                results.append(result)
                        
                        except Exception as e:
                            continue
                    
                    if results:
                        print(f"   ✅ {len(results)}건 수집")
                        break
                    
                except Exception as e:
                    print(f"   ⚠️ {instance} 실패, 다음 시도...")
                    continue
            
            if not results:
                print(f"   ⚠️ 모든 인스턴스 실패")
        
        except Exception as e:
            print(f"   ❌ 검색 실패: {e}")
        
        return results
    
    def _is_phishing_related(self, text: str) -> bool:
        """피싱 관련 트윗인지 확인"""
        phishing_keywords = [
            'phishing', 'scam', 'fraud', 'spam', 'smishing',
            'suspicious', 'fake', 'malicious', 'alert', 'warning',
            '피싱', '스미싱', '사기', '주의'
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in phishing_keywords)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """피싱 관련 키워드 추출"""
        keywords = []
        
        patterns = [
            r'phishing', r'scam', r'fraud', r'spam', r'smishing',
            r'suspicious', r'malicious', r'alert', r'warning',
            r'피싱', r'스미싱', r'사기', r'주의',
            r'#phishing', r'#scam', r'#cybersecurity'
        ]
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                keywords.append(pattern)
        
        return list(set(keywords))
    
    def save_to_json(self, data: List[Dict], filename: str = None):
        """JSON 파일로 저장"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'data/raw/twitter_{timestamp}.json'
        
        import os
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 저장 완료: {filename}")
    
    def run(self, queries: List[str] = None, max_results_per_query: int = 50):
        """전체 크롤링 실행"""
        if queries is None:
            queries = [
                'phishing alert',
                'scam warning',
                'phishing attack',
                'email scam',
                'smishing',
                '피싱 주의',
                '스미싱 경고',
                '보이스피싱'
            ]
        
        print(f"\n{'='*60}")
        print(f"🚀 X (Twitter) 크롤링 시작")
        print(f"   검색어: {len(queries)}개")
        print(f"{'='*60}")
        
        all_results = []
        
        for query in queries:
            results = self.search_twitter(query, max_results=max_results_per_query)
            all_results.extend(results)
            time.sleep(5)  # Rate limiting
        
        # 중복 제거
        unique_results = {}
        for result in all_results:
            content = result['content']
            if content not in unique_results:
                unique_results[content] = result
        
        final_results = list(unique_results.values())
        
        print(f"\n{'='*60}")
        print(f"✅ 크롤링 완료!")
        print(f"   전체 수집: {len(all_results)}건")
        print(f"   중복 제거: {len(final_results)}건")
        print(f"{'='*60}\n")
        
        return final_results


def main():
    crawler = TwitterPhishingCrawler()
    
    queries = [
        'phishing alert',
        'scam warning',
        'phishing attack',
        'smishing alert',
        '피싱 주의',
        '보이스피싱 경고'
    ]
    
    results = crawler.run(queries=queries, max_results_per_query=30)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    crawler.save_to_json(results, f'data/raw/twitter_{timestamp}.json')
    
    print("\n📊 수집 통계:")
    print(f"   총 트윗: {len(results)}건")


if __name__ == "__main__":
    main()
