"""
KISA 불법스팸대응센터 크롤러
- 공지사항, 주의 권고, 피싱 사례 수집
- JSON 형식으로 저장
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from typing import List, Dict
import time
from urllib.parse import urljoin

class KISASpamCrawler:
    def __init__(self):
        self.base_url = "https://spam.kisa.or.kr"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def crawl_notices(self, max_pages: int = 3) -> List[Dict]:
        """공지사항 크롤링"""
        notices = []
        
        for page in range(1, max_pages + 1):
            print(f"📄 공지사항 페이지 {page} 크롤링 중...")
            
            try:
                # 공지사항 목록 URL
                url = f"{self.base_url}/spam/sub61.do?boardType=NOTICE&page={page}"
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 게시글 목록 찾기
                posts = soup.find_all('tr')
                
                for post in posts:
                    try:
                        # 제목 링크 찾기
                        title_link = post.find('a')
                        if not title_link:
                            continue
                            
                        title = title_link.get_text(strip=True)
                        
                        # 피싱/스미싱 관련 게시글만 필터링
                        if not any(keyword in title for keyword in ['피싱', '스미싱', '주의', '경고', '권고']):
                            continue
                        
                        # 날짜 찾기
                        date_td = post.find('td', class_='date')
                        date = date_td.get_text(strip=True) if date_td else 'N/A'
                        
                        # 상세 페이지 URL
                        detail_url = title_link.get('href')
                        if detail_url and not detail_url.startswith('http'):
                            detail_url = urljoin(self.base_url, detail_url)
                        
                        notice = {
                            'id': f'notice_{len(notices) + 1}',
                            'source': 'KISA 불법스팸대응센터',
                            'category': '공지사항',
                            'title': title,
                            'date': date,
                            'url': detail_url,
                            'content': '',
                            'keywords': self._extract_keywords(title),
                            'crawled_at': datetime.now().isoformat()
                        }
                        
                        # 상세 내용 크롤링
                        if detail_url:
                            content = self._crawl_detail(detail_url)
                            notice['content'] = content
                        
                        notices.append(notice)
                        print(f"  ✓ 수집: {title[:50]}...")
                        
                        time.sleep(0.5)  # 서버 부하 방지
                        
                    except Exception as e:
                        print(f"  ✗ 게시글 처리 실패: {e}")
                        continue
                
                time.sleep(1)  # 페이지 간 대기
                
            except Exception as e:
                print(f"✗ 페이지 {page} 크롤링 실패: {e}")
                continue
        
        return notices
    
    def _crawl_detail(self, url: str) -> str:
        """상세 페이지 내용 크롤링"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 본문 내용 찾기 (여러 가능한 선택자 시도)
            content_div = soup.find('div', class_='board-view-content')
            if not content_div:
                content_div = soup.find('div', class_='view-content')
            if not content_div:
                content_div = soup.find('div', class_='content')
            
            if content_div:
                # 텍스트 추출 및 정리
                text = content_div.get_text(separator='\n', strip=True)
                return text
            
            return ''
            
        except Exception as e:
            print(f"  ✗ 상세 내용 크롤링 실패: {e}")
            return ''
    
    def _extract_keywords(self, text: str) -> List[str]:
        """키워드 추출"""
        keywords = []
        keyword_list = [
            '피싱', '스미싱', '보이스피싱', '큐싱',
            '쿠팡', '택배', '은행', '금융', '카드',
            '국세청', '경찰', '검찰', '법원', '우체국',
            'SKT', 'KT', 'LG', '통신사',
            '민생회복', '쿠폰', '지원금', '환급',
            '개인정보', '계좌', '비밀번호', '보안',
            '해킹', '악성앱', '링크'
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
        print("🚀 KISA 불법스팸대응센터 크롤링 시작\n")
        
        # 공지사항 크롤링
        notices = self.crawl_notices(max_pages=3)
        
        # 결과 저장
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.save_to_json(notices, f'kisa_notices_{timestamp}.json')
        
        # 통계 출력
        print("\n" + "="*50)
        print("📊 크롤링 통계")
        print("="*50)
        print(f"총 수집 건수: {len(notices)}건")
        
        if notices:
            print(f"\n최근 수집된 항목 (최대 5개):")
            for notice in notices[:5]:
                print(f"  • {notice['title'][:60]}...")
        
        return notices


if __name__ == "__main__":
    crawler = KISASpamCrawler()
    crawler.run()
