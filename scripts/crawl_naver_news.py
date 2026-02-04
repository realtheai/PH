import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from typing import List, Dict
import time
from urllib.parse import quote
import re

class NaverNewsCrawler:
    def __init__(self):
        self.base_url = "https://search.naver.com/search.naver"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def search_news(self, keyword: str, max_pages: int = 10) -> List[Dict]:
        """네이버 뉴스 검색"""
        results = []
        
        print(f"\n🔍 네이버 뉴스 검색: '{keyword}'")
        
        for page in range(1, max_pages + 1):
            try:
                start = (page - 1) * 10 + 1
                params = {
                    'where': 'news',
                    'query': keyword,
                    'start': start,
                    'sort': 'rel'  # 관련도순
                }
                
                response = self.session.get(self.base_url, params=params)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 뉴스 기사 목록
                news_items = soup.select('.news_area')
                
                if not news_items:
                    print(f"   ⚠️ {page}페이지: 기사 없음 (종료)")
                    break
                
                for item in news_items:
                    try:
                        # 제목과 링크
                        title_elem = item.select_one('.news_tit')
                        if not title_elem:
                            continue
                        
                        title = title_elem.get('title', '')
                        url = title_elem.get('href', '')
                        
                        # 요약 내용
                        content_elem = item.select_one('.news_dsc')
                        content = content_elem.get_text(strip=True) if content_elem else ''
                        
                        # 출처
                        source_elem = item.select_one('.info_group .press')
                        source = source_elem.get_text(strip=True) if source_elem else ''
                        
                        # 날짜
                        date_elem = item.select_one('.info_group span:last-child')
                        date = date_elem.get_text(strip=True) if date_elem else ''
                        
                        # 피싱 키워드 추출
                        keywords = self._extract_keywords(title + ' ' + content)
                        
                        result = {
                            'source': 'naver_news',
                            'keyword': keyword,
                            'title': title,
                            'url': url,
                            'content': content,
                            'press': source,
                            'date': date,
                            'extracted_keywords': keywords,
                            'crawled_at': datetime.now().isoformat()
                        }
                        
                        results.append(result)
                        
                    except Exception as e:
                        print(f"   ⚠️ 기사 파싱 실패: {e}")
                        continue
                
                print(f"   ✅ {page}페이지: {len(news_items)}건 수집")
                time.sleep(1)  # 요청 간격
                
            except Exception as e:
                print(f"   ❌ {page}페이지 크롤링 실패: {e}")
                break
        
        print(f"   📊 총 {len(results)}건 수집 완료\n")
        return results
    
    def crawl_article_detail(self, url: str) -> str:
        """기사 본문 상세 크롤링 (선택적)"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 네이버 뉴스 본문
            article = soup.select_one('#dic_area, #articeBody, .article_body')
            if article:
                # 스크립트, 광고 제거
                for tag in article.select('script, style, iframe'):
                    tag.decompose()
                
                content = article.get_text(strip=True)
                return content
            
            return ''
            
        except Exception as e:
            print(f"   ⚠️ 본문 크롤링 실패: {e}")
            return ''
    
    def _extract_keywords(self, text: str) -> List[str]:
        """피싱 관련 키워드 추출"""
        keywords = []
        
        patterns = [
            r'피싱', r'스미싱', r'보이스피싱', r'메신저피싱',
            r'계좌이체', r'금융사기', r'개인정보', r'비밀번호',
            r'공공기관\s*사칭', r'금융감독원', r'경찰청', r'검찰청',
            r'카드론', r'대출', r'환급금', r'보상금',
            r'긴급', r'승인', r'차단', r'정지', r'해제',
            r'링크', r'URL', r'앱\s*설치', r'다운로드',
            r'사칭', r'속여', r'기망', r'편취', r'편법',
            r'OTP', r'ARS', r'텔레뱅킹', r'모바일뱅킹'
        ]
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                keywords.append(pattern.replace(r'\s*', ' '))
        
        return list(set(keywords))
    
    def save_to_json(self, data: List[Dict], filename: str = None):
        """JSON 파일로 저장"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'data/raw/naver_news_{timestamp}.json'
        
        import os
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 저장 완료: {filename}")
    
    def run(self, keywords: List[str] = None, max_pages_per_keyword: int = 10):
        """전체 크롤링 실행"""
        if keywords is None:
            keywords = [
                '피싱 주의보',
                '스미싱 사례',
                '보이스피싱 피해',
                '금융사기 수법',
                '메신저피싱',
                '계좌이체 사기',
                '개인정보 탈취',
                '공공기관 사칭'
            ]
        
        print(f"\n{'='*60}")
        print(f"🚀 네이버 뉴스 크롤링 시작")
        print(f"   키워드: {len(keywords)}개")
        print(f"   페이지/키워드: 최대 {max_pages_per_keyword}페이지")
        print(f"{'='*60}")
        
        all_results = []
        
        for keyword in keywords:
            results = self.search_news(keyword, max_pages=max_pages_per_keyword)
            all_results.extend(results)
            time.sleep(2)  # 키워드 간 대기
        
        # 중복 제거 (URL 기준)
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
    crawler = NaverNewsCrawler()
    
    # 피싱 관련 키워드
    keywords = [
        '피싱 주의보',
        '스미싱 사례',
        '보이스피싱 피해',
        '금융사기 수법',
        '메신저피싱',
        '계좌이체 사기',
        '개인정보 탈취',
        '공공기관 사칭 피싱',
        '금융감독원 피싱',
        '택배 스미싱',
        '카드론 피싱',
        '환급금 사기'
    ]
    
    # 크롤링 실행 (키워드당 5페이지 = 약 50건)
    results = crawler.run(keywords=keywords, max_pages_per_keyword=5)
    
    # JSON 저장
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    crawler.save_to_json(results, f'data/raw/naver_news_{timestamp}.json')
    
    # 통계
    print("\n📊 수집 통계:")
    print(f"   총 기사: {len(results)}건")
    
    # 키워드별 통계
    keyword_stats = {}
    for result in results:
        kw = result['keyword']
        keyword_stats[kw] = keyword_stats.get(kw, 0) + 1
    
    print(f"\n   키워드별:")
    for kw, count in sorted(keyword_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"      - {kw}: {count}건")


if __name__ == "__main__":
    main()
