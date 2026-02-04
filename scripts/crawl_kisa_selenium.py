"""
Selenium 기반 KISA 불법스팸대응센터 크롤러
- JavaScript 렌더링 지원
- 실제 브라우저 환경에서 크롤링
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json
from datetime import datetime
from typing import List, Dict
import time

class KISASeleniumCrawler:
    def __init__(self, headless=True):
        self.base_url = "https://spam.kisa.or.kr"
        self.setup_driver(headless)
        
    def setup_driver(self, headless=True):
        """Chrome WebDriver 설정"""
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        self.wait = WebDriverWait(self.driver, 10)
        
    def crawl_main_page_notices(self) -> List[Dict]:
        """메인 페이지의 공지사항 크롤링"""
        notices = []
        
        try:
            print(f"🌐 KISA 메인 페이지 접속 중...")
            self.driver.get(f"{self.base_url}/spam/main.do")
            time.sleep(3)  # 페이지 로딩 대기
            
            # 페이지 소스 가져오기
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # 공지사항 섹션 찾기
            notice_items = soup.find_all('li')
            
            for idx, item in enumerate(notice_items, 1):
                try:
                    # 제목과 링크 찾기
                    link = item.find('a')
                    if not link:
                        continue
                    
                    title = link.get_text(strip=True)
                    
                    # 피싱 관련 게시글만 필터링
                    if not any(keyword in title for keyword in ['피싱', '스미싱', '주의', '권고', '보이스피싱']):
                        continue
                    
                    # 날짜 찾기
                    date_text = ''
                    for text in item.stripped_strings:
                        if '등록일' in text or '-' in text:
                            date_text = text.replace('등록일', '').strip()
                            break
                    
                    # URL 추출
                    href = link.get('href', '')
                    detail_url = ''
                    if href:
                        if href.startswith('http'):
                            detail_url = href
                        elif href.startswith('/'):
                            detail_url = self.base_url + href
                    
                    notice = {
                        'id': f'kisa_main_{idx}',
                        'source': 'KISA 불법스팸대응센터',
                        'category': '공지사항',
                        'title': title,
                        'date': date_text,
                        'url': detail_url,
                        'content': '',
                        'keywords': self._extract_keywords(title),
                        'crawled_at': datetime.now().isoformat()
                    }
                    
                    notices.append(notice)
                    print(f"  ✓ 수집: {title[:60]}...")
                    
                except Exception as e:
                    print(f"  ✗ 항목 처리 실패: {e}")
                    continue
            
        except Exception as e:
            print(f"✗ 메인 페이지 크롤링 실패: {e}")
        
        return notices
    
    def crawl_notice_detail(self, url: str) -> str:
        """상세 페이지 내용 크롤링"""
        try:
            self.driver.get(url)
            time.sleep(2)
            
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # 본문 내용 찾기
            content_div = soup.find('div', class_='board-view-content')
            if not content_div:
                content_div = soup.find('div', class_='view-content')
            if not content_div:
                content_div = soup.find('div', class_='content')
            
            if content_div:
                return content_div.get_text(separator='\n', strip=True)
            
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
            '해킹', '악성앱', '링크', 'KISA'
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
        print("🚀 KISA Selenium 크롤러 시작\n")
        
        try:
            # 메인 페이지 공지사항 크롤링
            notices = self.crawl_main_page_notices()
            
            if notices:
                # 결과 저장
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                self.save_to_json(notices, f'kisa_selenium_{timestamp}.json')
                
                # 통계 출력
                print("\n" + "="*50)
                print("📊 크롤링 통계")
                print("="*50)
                print(f"총 수집 건수: {len(notices)}건")
                
                # 키워드 통계
                all_keywords = []
                for notice in notices:
                    all_keywords.extend(notice['keywords'])
                
                if all_keywords:
                    from collections import Counter
                    keyword_counts = Counter(all_keywords)
                    print(f"\n🔑 주요 키워드 (Top 10):")
                    for keyword, count in keyword_counts.most_common(10):
                        print(f"   • {keyword}: {count}회")
            else:
                print("⚠️  수집된 데이터가 없습니다.")
            
            return notices
            
        except Exception as e:
            print(f"✗ 크롤링 실패: {e}")
            return []
        
        finally:
            self.driver.quit()


if __name__ == "__main__":
    crawler = KISASeleniumCrawler(headless=True)
    crawler.run()
