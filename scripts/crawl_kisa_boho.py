"""
KISA 보호나라 크롤러
- 보안공지, 가이드, 피싱 관련 정보 수집
- JSON 형식으로 저장
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from typing import List, Dict
import time
from urllib.parse import urljoin

class KISABohoCrawler:
    def __init__(self):
        self.base_url = "https://www.boho.or.kr"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def crawl_security_notices(self, max_items: int = 20) -> List[Dict]:
        """보안공지 크롤링"""
        notices = []
        
        print(f"🔒 보안공지 크롤링 중...")
        
        try:
            # 보안공지 페이지
            url = f"{self.base_url}/data/secNoticeList.do"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 게시글 목록 찾기
            posts = soup.find_all('li', limit=max_items)
            
            for idx, post in enumerate(posts, 1):
                try:
                    # 제목 링크 찾기
                    title_link = post.find('a')
                    if not title_link:
                        continue
                    
                    title = title_link.get_text(strip=True)
                    
                    # 피싱 관련 게시글 필터링
                    if not any(keyword in title for keyword in ['피싱', '스미싱', '보이스피싱']):
                        continue
                    
                    # 날짜 찾기
                    date_span = post.find('span', class_='date')
                    date = date_span.get_text(strip=True) if date_span else 'N/A'
                    
                    # URL
                    detail_url = title_link.get('href')
                    if detail_url and not detail_url.startswith('http'):
                        detail_url = urljoin(self.base_url, detail_url)
                    
                    notice = {
                        'id': f'boho_notice_{idx}',
                        'source': 'KISA 보호나라',
                        'category': '보안공지',
                        'title': title,
                        'date': date,
                        'url': detail_url,
                        'content': '',
                        'keywords': self._extract_keywords(title),
                        'crawled_at': datetime.now().isoformat()
                    }
                    
                    notices.append(notice)
                    print(f"  ✓ 수집: {title[:50]}...")
                    
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"  ✗ 게시글 처리 실패: {e}")
                    continue
            
        except Exception as e:
            print(f"✗ 보안공지 크롤링 실패: {e}")
        
        return notices
    
    def _extract_keywords(self, text: str) -> List[str]:
        """키워드 추출"""
        keywords = []
        keyword_list = [
            '피싱', '스미싱', '보이스피싱', '큐싱',
            '악성코드', '해킹', '랜섬웨어',
            '개인정보', '금융사기', '보안위협'
        ]
        
        for keyword in keyword_list:
            if keyword in text:
                keywords.append(keyword)
        
        return keywords
    
    def save_to_json(self, data: List[Dict], filename: str):
        """JSON 파일로 저장"""
        filepath = f"data/raw/{filename}"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 데이터 저장 완료: {filepath}")
        print(f"   총 {len(data)}건 수집됨")
    
    def run(self):
        """크롤링 실행"""
        print("🚀 KISA 보호나라 크롤링 시작\n")
        
        # 보안공지 크롤링
        notices = self.crawl_security_notices(max_items=20)
        
        # 결과 저장
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.save_to_json(notices, f'kisa_boho_{timestamp}.json')
        
        # 통계 출력
        print("\n" + "="*50)
        print("📊 크롤링 통계")
        print("="*50)
        print(f"총 수집 건수: {len(notices)}건")
        
        if notices:
            print(f"\n최근 수집된 항목:")
            for notice in notices[:5]:
                print(f"  • {notice['title'][:60]}...")
        
        return notices


if __name__ == "__main__":
    crawler = KISABohoCrawler()
    crawler.run()
