import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from typing import List, Dict
import time
from urllib.parse import quote, urljoin
import re
from newspaper import Article

class GoogleNewsCrawler:
    def __init__(self):
        self.base_url = "https://www.google.com/search"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def fetch_full_content(self, url: str) -> str:
        """URL에서 전체 기사 본문 추출 (newspaper3k 사용)"""
        try:
            article = Article(url, language='ko')
            article.download()
            article.parse()
            return article.text if article.text else ""
        except Exception as e:
            print(f"      ⚠️ 본문 추출 실패: {e}")
            return ""
    
    def search_news(self, keyword: str, max_results: int = 50) -> List[Dict]:
        """구글 뉴스 검색"""
        results = []
        
        print(f"\n🔍 구글 뉴스 검색: '{keyword}'")
        
        try:
            # 구글 뉴스 검색 (한국어, 최근 1년)
            params = {
                'q': keyword,
                'tbm': 'nws',  # 뉴스 검색
                'hl': 'ko',     # 한국어
                'gl': 'kr',     # 한국
                'num': min(max_results, 100)  # 최대 100개
            }
            
            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 뉴스 기사 목록
            news_items = soup.select('.SoaBEf, .WlydOe, div[data-hveid]')
            
            if not news_items:
                # 대체 셀렉터
                news_items = soup.select('.Gx5Zad')
            
            print(f"   📄 발견된 요소: {len(news_items)}개")
            
            for idx, item in enumerate(news_items, 1):
                try:
                    # 제목
                    title_elem = item.select_one('.mCBkyc, .n0jPhd, .JheGif')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    
                    # 링크
                    link_elem = item.select_one('a')
                    if not link_elem:
                        continue
                    
                    url = link_elem.get('href', '')
                    if url.startswith('/url?q='):
                        url = url.split('/url?q=')[1].split('&')[0]
                    
                    # 출처
                    source_elem = item.select_one('.NUnG9d span, .CEMjEf')
                    source = source_elem.get_text(strip=True) if source_elem else ''
                    
                    # 날짜
                    date_elem = item.select_one('.LfVVr, .OSrXXb span')
                    date = date_elem.get_text(strip=True) if date_elem else ''
                    
                    # 전체 본문 추출
                    print(f"      [{idx}/{len(news_items)}] 본문 추출 중...", end=' ')
                    full_content = self.fetch_full_content(url)
                    
                    if full_content:
                        print(f"✅ ({len(full_content)}자)")
                        content = full_content
                    else:
                        # 요약문이라도 저장
                        content_elem = item.select_one('.GI74Re, .Y3v8qd')
                        content = content_elem.get_text(strip=True) if content_elem else ''
                        print(f"⚠️ 요약만 사용 ({len(content)}자)")
                    
                    # 피싱 키워드 추출
                    keywords = self._extract_keywords(title + ' ' + content)
                    
                    result = {
                        'source': 'google_news',
                        'keyword': keyword,
                        'title': title,
                        'url': url,
                        'content': content,
                        'content_length': len(content),
                        'press': source,
                        'date': date,
                        'extracted_keywords': keywords,
                        'crawled_at': datetime.now().isoformat()
                    }
                    
                    results.append(result)
                    time.sleep(0.5)  # 서버 부하 방지
                    
                except Exception as e:
                    print(f"   ⚠️ 기사 파싱 실패: {e}")
                    continue
            
            print(f"   ✅ {len(results)}건 수집 완료\n")
            
        except Exception as e:
            print(f"   ❌ 검색 실패: {e}")
        
        return results
    
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
            r'OTP', r'ARS', r'텔레뱅킹', r'모바일뱅킹',
            r'택배', r'배송', r'우체국', r'택배조회',
            r'phishing', r'smishing', r'scam', r'fraud'
        ]
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                keywords.append(pattern.replace(r'\s*', ' '))
        
        return list(set(keywords))
    
    def save_to_json(self, data: List[Dict], filename: str = None):
        """JSON 파일로 저장"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'data/raw/google_news_{timestamp}.json'
        
        import os
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 저장 완료: {filename}")
    
    def run(self, keywords: List[str] = None, max_results_per_keyword: int = 50):
        """전체 크롤링 실행"""
        if keywords is None:
            keywords = [
                '피싱 사례 한국',
                '스미싱 주의',
                '보이스피싱 수법',
                '금융사기 피해',
                '메신저 피싱',
                '택배 스미싱',
                '공공기관 사칭',
                '개인정보 탈취'
            ]
        
        print(f"\n{'='*60}")
        print(f"🚀 구글 뉴스 크롤링 시작")
        print(f"   키워드: {len(keywords)}개")
        print(f"   결과/키워드: 최대 {max_results_per_keyword}건")
        print(f"{'='*60}")
        
        all_results = []
        
        for keyword in keywords:
            results = self.search_news(keyword, max_results=max_results_per_keyword)
            all_results.extend(results)
            time.sleep(3)  # 요청 간격 (구글 차단 방지)
        
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
    crawler = GoogleNewsCrawler()
    
    # 피싱 관련 키워드 (최신 수법 포함 - 28개)
    keywords = [
        '피싱 주의보',
        '스미싱 사례',
        '보이스피싱 피해',
        '금융사기 수법',
        '메신저피싱',
        '계좌이체 사기',
        '개인정보 탈취',
        '공공기관 사칭 피싱',
        '택배 스미싱',
        '카드론 피싱',
        '환급금 사기',
        '금융감독원 피싱',
        '딸 사칭 문자',
        '아들 사칭 피싱',
        '액정 파손 문자 스미싱',
        '핸드폰 고장 문자 사기',
        '부고 문자 스미싱',
        '모바일 청첩장 피싱',
        '건강검진 결과 문자 사기',
        '교통범칙금 과태료 조회 스미싱',
        '에너지바우처 환급 피싱',
        '민생지원금 대상자 문자',
        '검찰청 출석요구서 스미싱',
        '우체국 미수령 택배 안내',
        '해외결제 완료 문자 사기',
        '쓰레기 무단투기 과태료 문자',
        '주식 리딩방 가입 유도 사기',
        '대출 승인 문자 피싱'
    ]
    
    # 날짜 범위
    start_date = '2025-02-01'
    end_date = '2026-01-31'
    
    print(f"\n{'='*60}")
    print(f"📅 구글 뉴스 크롤링 (2025-02-01 ~ 2026-01-31)")
    print(f"   키워드: {len(keywords)}개")
    print(f"{'='*60}")
    
    # 크롤링 실행
    results = crawler.run(keywords=keywords, max_results_per_keyword=50)
    
    # JSON 저장
    filename = f'data/raw/google_news_{start_date}_to_{end_date}.json'
    crawler.save_to_json(results, filename)
    
    print(f"\n✅ 저장 완료: {filename}")
    print(f"   총 {len(results)}건 수집")
    
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
