"""
해외 뉴스 피싱 사례 크롤러
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from typing import List, Dict
import time
import re

class InternationalNewsCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def search_bbc_news(self, query: str = 'phishing', max_results: int = 20) -> List[Dict]:
        """BBC 뉴스 검색"""
        results = []
        
        print(f"\n🔍 BBC News 검색: '{query}'")
        
        try:
            url = "https://www.bbc.com/search"
            params = {
                'q': query,
                'filter': 'news'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.select('[data-testid="card-headline"]')[:max_results]
            
            for article in articles:
                try:
                    # 제목
                    title = article.get_text(strip=True)
                    
                    # 링크
                    link = article.find_parent('a')
                    url = 'https://www.bbc.com' + link.get('href', '') if link else ''
                    
                    if self._is_phishing_related(title):
                        result = {
                            'source': 'bbc_news',
                            'query': query,
                            'title': title,
                            'url': url,
                            'content': '',
                            'extracted_keywords': self._extract_keywords(title),
                            'crawled_at': datetime.now().isoformat()
                        }
                        results.append(result)
                
                except Exception as e:
                    continue
            
            print(f"   ✅ {len(results)}건 수집")
        
        except Exception as e:
            print(f"   ❌ 검색 실패: {e}")
        
        return results
    
    def search_reuters(self, query: str = 'phishing', max_results: int = 20) -> List[Dict]:
        """Reuters 뉴스 검색"""
        results = []
        
        print(f"\n🔍 Reuters 검색: '{query}'")
        
        try:
            url = "https://www.reuters.com/site-search/"
            params = {'query': query}
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.select('.search-result-title')[:max_results]
            
            for article in articles:
                try:
                    # 제목
                    title_elem = article.select_one('a')
                    title = title_elem.get_text(strip=True) if title_elem else ''
                    url = title_elem.get('href', '') if title_elem else ''
                    
                    if self._is_phishing_related(title):
                        result = {
                            'source': 'reuters',
                            'query': query,
                            'title': title,
                            'url': url,
                            'content': '',
                            'extracted_keywords': self._extract_keywords(title),
                            'crawled_at': datetime.now().isoformat()
                        }
                        results.append(result)
                
                except Exception as e:
                    continue
            
            print(f"   ✅ {len(results)}건 수집")
        
        except Exception as e:
            print(f"   ❌ 검색 실패: {e}")
        
        return results
    
    def search_bing_news(self, query: str, max_results: int = 30) -> List[Dict]:
        """Bing 뉴스 검색"""
        results = []
        
        print(f"\n🔍 Bing News 검색: '{query}'")
        
        try:
            url = "https://www.bing.com/news/search"
            params = {
                'q': query,
                'qft': 'sortbydate'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.select('.news-card')[:max_results]
            
            for article in articles:
                try:
                    # 제목
                    title_elem = article.select_one('.title')
                    title = title_elem.get_text(strip=True) if title_elem else ''
                    
                    # 링크
                    link_elem = article.select_one('a')
                    url = link_elem.get('href', '') if link_elem else ''
                    
                    # 요약
                    snippet_elem = article.select_one('.snippet')
                    content = snippet_elem.get_text(strip=True) if snippet_elem else ''
                    
                    # 출처
                    source_elem = article.select_one('.source')
                    source = source_elem.get_text(strip=True) if source_elem else ''
                    
                    if self._is_phishing_related(title + ' ' + content):
                        result = {
                            'source': 'bing_news',
                            'query': query,
                            'title': title,
                            'url': url,
                            'content': content,
                            'press': source,
                            'extracted_keywords': self._extract_keywords(title + ' ' + content),
                            'crawled_at': datetime.now().isoformat()
                        }
                        results.append(result)
                
                except Exception as e:
                    continue
            
            print(f"   ✅ {len(results)}건 수집")
        
        except Exception as e:
            print(f"   ❌ 검색 실패: {e}")
        
        return results
    
    def _is_phishing_related(self, text: str) -> bool:
        """피싱 관련 기사인지 확인"""
        phishing_keywords = [
            'phishing', 'scam', 'fraud', 'spam', 'smishing',
            'cyber', 'hack', 'breach', 'malware', 'ransomware'
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in phishing_keywords)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """피싱 관련 키워드 추출"""
        keywords = []
        
        patterns = [
            r'phishing', r'scam', r'fraud', r'spam', r'smishing',
            r'cyber', r'hack', r'breach', r'malware', r'ransomware',
            r'email', r'bank', r'account', r'password', r'credential'
        ]
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                keywords.append(pattern)
        
        return list(set(keywords))
    
    def save_to_json(self, data: List[Dict], filename: str = None):
        """JSON 파일로 저장"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'data/raw/intl_news_{timestamp}.json'
        
        import os
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 저장 완료: {filename}")
    
    def run(self, queries: List[str] = None):
        """전체 크롤링 실행"""
        if queries is None:
            queries = [
                'phishing attack',
                'email scam',
                'online fraud',
                'smishing',
                'cyber scam',
                'voice phishing script',
                'deepfake audio scam',
                'pig butchering scam',
                'identity theft cases',
                'bank impersonation fraud',
                'remote access scam',
                'technical support scam'
            ]
        
        print(f"\n{'='*60}")
        print(f"🚀 해외 뉴스 크롤링 시작")
        print(f"   검색어: {len(queries)}개")
        print(f"{'='*60}")
        
        all_results = []
        
        for query in queries:
            # Bing 뉴스 (가장 안정적)
            results = self.search_bing_news(query, max_results=20)
            all_results.extend(results)
            time.sleep(3)
        
        # 중복 제거
        unique_results = {}
        for result in all_results:
            url = result['url']
            if url and url not in unique_results:
                unique_results[url] = result
        
        final_results = list(unique_results.values())
        
        print(f"\n{'='*60}")
        print(f"✅ 크롤링 완료!")
        print(f"   전체 수집: {len(all_results)}건")
        print(f"   중복 제거: {len(final_results)}건")
        print(f"{'='*60}\n")
        
        return final_results


def main():
    crawler = InternationalNewsCrawler()
    
    queries = [
        'phishing attack',
        'email scam 2026',
        'online fraud',
        'smishing alert',
        'cyber scam warning'
    ]
    
    results = crawler.run(queries=queries)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    crawler.save_to_json(results, f'data/raw/intl_news_{timestamp}.json')
    
    print("\n📊 수집 통계:")
    print(f"   총 기사: {len(results)}건")


if __name__ == "__main__":
    main()
