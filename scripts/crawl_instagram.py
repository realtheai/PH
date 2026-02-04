"""
Instagram 피싱 경고 게시물 크롤러
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from typing import List, Dict
import time
import re

class InstagramPhishingCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def search_hashtag(self, hashtag: str, max_results: int = 30) -> List[Dict]:
        """해시태그로 검색 (Picuki 사용)"""
        results = []
        
        print(f"\n🔍 Instagram 검색: #{hashtag}")
        
        try:
            # Picuki (Instagram viewer) 사용
            url = f"https://www.picuki.com/tag/{hashtag}"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            posts = soup.select('.box-photos .item')
            
            for post in posts[:max_results]:
                try:
                    # 이미지/썸네일
                    img_elem = post.select_one('img')
                    img_url = img_elem.get('src', '') if img_elem else ''
                    
                    # 캡션
                    caption_elem = post.select_one('.photo-description')
                    caption = caption_elem.get_text(strip=True) if caption_elem else ''
                    
                    # 링크
                    link_elem = post.select_one('a')
                    post_url = 'https://www.picuki.com' + link_elem.get('href', '') if link_elem else ''
                    
                    # 좋아요/댓글
                    likes_elem = post.select_one('.likes')
                    likes = likes_elem.get_text(strip=True) if likes_elem else '0'
                    
                    if self._is_phishing_related(caption):
                        result = {
                            'source': 'instagram',
                            'hashtag': hashtag,
                            'caption': caption,
                            'url': post_url,
                            'image_url': img_url,
                            'likes': likes,
                            'extracted_keywords': self._extract_keywords(caption),
                            'crawled_at': datetime.now().isoformat()
                        }
                        results.append(result)
                
                except Exception as e:
                    continue
            
            print(f"   ✅ {len(results)}건 수집")
            time.sleep(2)
        
        except Exception as e:
            print(f"   ❌ 검색 실패: {e}")
        
        return results
    
    def _is_phishing_related(self, text: str) -> bool:
        """피싱 관련 게시물인지 확인"""
        phishing_keywords = [
            'phishing', 'scam', 'fraud', 'spam', 'smishing',
            'suspicious', 'fake', 'warning', 'alert', 'beware',
            '피싱', '스미싱', '사기', '주의', '경고'
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in phishing_keywords)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """피싱 관련 키워드 추출"""
        keywords = []
        
        patterns = [
            r'phishing', r'scam', r'fraud', r'spam', r'smishing',
            r'suspicious', r'fake', r'warning', r'alert',
            r'피싱', r'스미싱', r'사기', r'주의',
            r'#phishing', r'#scam', r'#fraud'
        ]
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                keywords.append(pattern)
        
        return list(set(keywords))
    
    def save_to_json(self, data: List[Dict], filename: str = None):
        """JSON 파일로 저장"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'data/raw/instagram_{timestamp}.json'
        
        import os
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 저장 완료: {filename}")
    
    def run(self, hashtags: List[str] = None, max_results_per_tag: int = 30):
        """전체 크롤링 실행"""
        if hashtags is None:
            hashtags = [
                'phishing',
                'scam',
                'cybersecurity',
                'fraud',
                'emailscam',
                'smishing',
                '피싱',
                '스미싱',
                '보이스피싱'
            ]
        
        print(f"\n{'='*60}")
        print(f"🚀 Instagram 크롤링 시작")
        print(f"   해시태그: {len(hashtags)}개")
        print(f"{'='*60}")
        
        all_results = []
        
        for hashtag in hashtags:
            results = self.search_hashtag(hashtag, max_results=max_results_per_tag)
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
    crawler = InstagramPhishingCrawler()
    
    hashtags = [
        'phishing',
        'scam',
        'cybersecurity',
        'fraud',
        'smishing',
        '피싱주의',
        '보이스피싱'
    ]
    
    results = crawler.run(hashtags=hashtags, max_results_per_tag=20)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    crawler.save_to_json(results, f'data/raw/instagram_{timestamp}.json')
    
    print("\n📊 수집 통계:")
    print(f"   총 게시물: {len(results)}건")


if __name__ == "__main__":
    main()
