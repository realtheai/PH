"""
Reddit 피싱 관련 게시물 크롤러
"""

import requests
import json
from datetime import datetime
from typing import List, Dict
import time
import re

class RedditPhishingCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'PhishingApp/1.0 (by /u/phishing_researcher)'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def search_subreddit(self, subreddit: str, query: str = None, limit: int = 100) -> List[Dict]:
        """서브레딧에서 게시물 검색"""
        results = []
        
        print(f"\n🔍 Reddit 검색: r/{subreddit}")
        
        try:
            if query:
                # 검색 모드
                url = f"https://www.reddit.com/r/{subreddit}/search.json"
                params = {
                    'q': query,
                    'restrict_sr': 'on',
                    'sort': 'relevance',
                    'limit': limit
                }
            else:
                # Hot posts 모드
                url = f"https://www.reddit.com/r/{subreddit}/hot.json"
                params = {'limit': limit}
            
            response = self.session.get(url, params=params, timeout=15)
            
            # 403 에러 시 재시도
            if response.status_code == 403:
                time.sleep(5)
                response = self.session.get(url, params=params, timeout=15)
            
            response.raise_for_status()
            
            data = response.json()
            posts = data.get('data', {}).get('children', [])
            
            for post in posts:
                post_data = post.get('data', {})
                
                # 피싱 관련 키워드 확인
                title = post_data.get('title', '')
                selftext = post_data.get('selftext', '')
                
                if self._is_phishing_related(title + ' ' + selftext):
                    result = {
                        'source': 'reddit',
                        'subreddit': subreddit,
                        'title': title,
                        'content': selftext,
                        'url': f"https://www.reddit.com{post_data.get('permalink', '')}",
                        'author': post_data.get('author', ''),
                        'score': post_data.get('score', 0),
                        'num_comments': post_data.get('num_comments', 0),
                        'created_utc': post_data.get('created_utc', 0),
                        'flair': post_data.get('link_flair_text', ''),
                        'extracted_keywords': self._extract_keywords(title + ' ' + selftext),
                        'crawled_at': datetime.now().isoformat()
                    }
                    results.append(result)
            
            print(f"   ✅ {len(results)}건 수집")
            time.sleep(2)  # Rate limiting
            
        except Exception as e:
            print(f"   ❌ 크롤링 실패: {e}")
        
        return results
    
    def _is_phishing_related(self, text: str) -> bool:
        """피싱 관련 게시물인지 확인"""
        phishing_keywords = [
            'phishing', 'scam', 'fraud', 'spam', 'smishing',
            'suspicious', 'fake', 'malicious', 'threat',
            '피싱', '스미싱', '사기', '스팸'
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in phishing_keywords)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """피싱 관련 키워드 추출"""
        keywords = []
        
        patterns = [
            r'phishing', r'scam', r'fraud', r'spam', r'smishing',
            r'suspicious', r'malicious', r'threat', r'fake',
            r'피싱', r'스미싱', r'사기', r'스팸',
            r'email', r'link', r'attachment', r'password',
            r'account', r'verify', r'urgent', r'suspended'
        ]
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                keywords.append(pattern)
        
        return list(set(keywords))
    
    def save_to_json(self, data: List[Dict], filename: str = None):
        """JSON 파일로 저장"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'data/raw/reddit_{timestamp}.json'
        
        import os
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 저장 완료: {filename}")
    
    def run(self, subreddits: List[str] = None, limit_per_sub: int = 100):
        """전체 크롤링 실행"""
        if subreddits is None:
            subreddits = [
                'Scams',           # 사기 전문
                'phishing',        # 피싱 전문
                'cybersecurity',   # 사이버 보안
                'Fraud',           # 금융 사기
                'EmailScams',      # 이메일 사기
                'technology',      # 기술 (피싱 관련)
                'security',        # 보안
                'privacy',         # 개인정보
                'korea',           # 한국 관련
                'InformationSecurity',  # 정보 보안
                'SocialEngineering',    # 사회공학
                'DeepfakeScams'         # 딥페이크 사기
            ]
        
        print(f"\n{'='*60}")
        print(f"🚀 Reddit 크롤링 시작")
        print(f"   서브레딧: {len(subreddits)}개")
        print(f"   게시물/서브레딧: 최대 {limit_per_sub}개")
        print(f"{'='*60}")
        
        all_results = []
        
        for subreddit in subreddits:
            results = self.search_subreddit(subreddit, limit=limit_per_sub)
            all_results.extend(results)
            time.sleep(3)  # Rate limiting
        
        # 중복 제거
        unique_results = {}
        for result in all_results:
            url = result['url']
            if url not in unique_results:
                unique_results[url] = result
        
        final_results = list(unique_results.values())
        
        print(f"\n{'='*60}")
        print(f"✅ 크롤링 완료!")
        print(f"   전체 수집: {len(all_results)}건")
        print(f"   중복 제거: {len(final_results)}건")
        print(f"{'='*60}\n")
        
        return final_results


def main():
    crawler = RedditPhishingCrawler()
    
    # 주요 서브레딧 (11개 - Fraud 제거)
    subreddits = [
        'Scams',
        'phishing',
        'cybersecurity',
        'EmailScams',
        'technology',
        'security',
        'privacy',
        'korea',
        'InformationSecurity',
        'SocialEngineering',
        'DeepfakeScams'
    ]
    
    # 날짜 범위
    start_date = '2025-02-01'
    end_date = '2026-01-31'
    
    print(f"\n{'='*60}")
    print(f"📅 Reddit 크롤링 (2025-02-01 ~ 2026-01-31)")
    print(f"   서브레딧: {len(subreddits)}개")
    print(f"{'='*60}")
    
    results = crawler.run(subreddits=subreddits, limit_per_sub=100)
    
    # JSON 저장
    filename = f'data/raw/reddit_{start_date}_to_{end_date}.json'
    crawler.save_to_json(results, filename)
    
    print(f"\n✅ 저장 완료: {filename}")
    print(f"   총 {len(results)}건 수집")
    
    # 서브레딧별 통계
    subreddit_stats = {}
    for result in results:
        sub = result['subreddit']
        subreddit_stats[sub] = subreddit_stats.get(sub, 0) + 1
    
    print(f"\n📊 서브레딧별:")
    for sub, count in sorted(subreddit_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"      - r/{sub}: {count}건")


if __name__ == "__main__":
    main()
