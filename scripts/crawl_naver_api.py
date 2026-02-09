"""
네이버 검색 API를 사용한 뉴스 크롤러
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict
import time
import re
from dotenv import load_dotenv
import os
from newspaper import Article

# .env 파일 로드
load_dotenv()

class NaverAPINewsCrawler:
    def __init__(self):
        self.client_id = os.getenv('NAVER_CLIENT_ID')
        self.client_secret = os.getenv('NAVER_CLIENT_SECRET')
        
        if not self.client_id or not self.client_secret:
            raise ValueError("NAVER_CLIENT_ID와 NAVER_CLIENT_SECRET을 .env 파일에 설정해주세요.")
        
        self.headers = {
            'X-Naver-Client-Id': self.client_id,
            'X-Naver-Client-Secret': self.client_secret
        }
        self.base_url = "https://openapi.naver.com/v1/search/news.json"
    
    def fetch_full_content(self, url: str) -> str:
        """URL에서 전체 기사 본문 추출 (newspaper3k 사용)
        
        ⚠️ GitHub Actions 시간 절약을 위해 비활성화됨
        네이버 API description으로 충분함
        """
        # GitHub Actions 최적화: 본문 크롤링 비활성화
        # return ""  # 빠른 실행을 위해 스킵
        
        # 로컬에서만 전체 본문 크롤링 (선택적)
        try:
            article = Article(url, language='ko')
            article.download()
            article.parse()
            return article.text if article.text else ""
        except Exception as e:
            print(f"      ⚠️ 본문 추출 실패 ({url[:50]}...): {e}")
            return ""
    
    def search_news(self, query: str, display: int = 100, start: int = 1, start_date: str = None, end_date: str = None) -> List[Dict]:
        """네이버 뉴스 API 검색 (날짜 필터링 포함)"""
        results = []
        
        print(f"\n🔍 네이버 API 뉴스 검색: '{query}'")
        if start_date and end_date:
            print(f"   📅 기간: {start_date} ~ {end_date}")
        
        try:
            params = {
                'query': query,
                'display': display,  # 한 번에 가져올 개수 (최대 100)
                'start': start,       # 시작 위치
                'sort': 'date'        # 날짜순 정렬
            }
            
            response = requests.get(
                self.base_url,
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            items = data.get('items', [])
            
            for idx, item in enumerate(items, 1):
                # HTML 태그 제거
                title = self._remove_html_tags(item.get('title', ''))
                description = self._remove_html_tags(item.get('description', ''))
                url = item.get('link', '')
                pub_date = item.get('pubDate', '')
                
                # 날짜 필터링 (네이버 API는 RFC822 형식: "Mon, 30 Jan 2023 10:00:00 +0900")
                if start_date and end_date:
                    try:
                        from email.utils import parsedate_to_datetime
                        article_date = parsedate_to_datetime(pub_date)
                        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                        end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                        
                        if not (start_dt <= article_date <= end_dt):
                            continue
                    except:
                        pass
                
                # 전체 본문 추출 (GitHub Actions 최적화: API description 사용)
                # print(f"      [{idx}/{len(items)}] 본문 추출 중...", end=' ')
                # full_content = self.fetch_full_content(url)
                
                # GitHub Actions 시간 절약: API description 직접 사용
                content = description  # 네이버 API 요약문 사용 (충분함)
                print(f"      [{idx}/{len(items)}] ✅ ({len(content)}자)")
                
                # 피싱 관련 키워드 추출
                keywords = self._extract_keywords(title + ' ' + content)
                
                result = {
                    'source': 'naver_api',
                    'keyword': query,
                    'title': title,
                    'url': url,
                    'content': content,
                    'content_length': len(content),
                    'press': item.get('originallink', ''),
                    'date': pub_date,
                    'extracted_keywords': keywords,
                    'crawled_at': datetime.now().isoformat()
                }
                
                results.append(result)
                time.sleep(0.5)  # 서버 부하 방지
            
            print(f"   ✅ {len(results)}건 수집 완료")
            
        except requests.exceptions.HTTPError as e:
            print(f"   ❌ API 오류: {e}")
            if e.response.status_code == 401:
                print(f"   ⚠️ 인증 실패: NAVER_CLIENT_ID 또는 NAVER_CLIENT_SECRET을 확인하세요.")
            elif e.response.status_code == 429:
                print(f"   ⚠️ API 호출 한도 초과: 잠시 후 다시 시도하세요.")
        except Exception as e:
            print(f"   ❌ 검색 실패: {e}")
        
        return results
    
    def _remove_html_tags(self, text: str) -> str:
        """HTML 태그 제거"""
        # <b>, </b> 등 HTML 태그 제거
        text = re.sub(r'<[^>]+>', '', text)
        # HTML 엔티티 변환
        text = text.replace('&quot;', '"')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&nbsp;', ' ')
        return text.strip()
    
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
            r'택배', r'배송', r'우체국', r'택배조회'
        ]
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                keywords.append(pattern.replace(r'\s*', ' '))
        
        return list(set(keywords))
    
    def save_to_json(self, data: List[Dict], filename: str = None):
        """JSON 파일로 저장"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'data/raw/naver_api_{timestamp}.json'
        
        import os
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 저장 완료: {filename}")
    
    def run(self, keywords: List[str] = None, display_per_keyword: int = 100):
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
                '공공기관 사칭',
                '택배 스미싱',
                '카드론 피싱',
                '환급금 사기',
                '금융감독원 피싱'
            ]
        
        print(f"\n{'='*60}")
        print(f"🚀 네이버 API 뉴스 크롤링 시작")
        print(f"   키워드: {len(keywords)}개")
        print(f"   결과/키워드: 최대 {display_per_keyword}개")
        print(f"{'='*60}")
        
        all_results = []
        
        for keyword in keywords:
            results = self.search_news(keyword, display=display_per_keyword)
            all_results.extend(results)
            time.sleep(0.5)  # API 호출 간격 (네이버는 하루 25,000건까지 무료)
        
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
    try:
        crawler = NaverAPINewsCrawler()
        
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
        
        # 날짜 범위 설정 (2025-02-01 ~ 2026-01-31)
        start_date = '2025-02-01'
        end_date = '2026-01-31'
        
        print(f"\n{'='*60}")
        print(f"📅 네이버 API 크롤링 (날짜 범위 필터링)")
        print(f"   기간: {start_date} ~ {end_date}")
        print(f"   키워드: {len(keywords)}개")
        print(f"{'='*60}")
        
        all_results = []
        
        for keyword in keywords:
            results = crawler.search_news(keyword, display=100, start=1, 
                                         start_date=start_date, end_date=end_date)
            all_results.extend(results)
            time.sleep(1)  # API 요청 간격
        
        # 중복 제거 (URL 기준)
        unique_results = {}
        for result in all_results:
            url = result['url']
            if url not in unique_results:
                unique_results[url] = result
        
        final_results = list(unique_results.values())
        
        # JSON 저장 (파일명에 날짜 범위 포함)
        filename = f'data/raw/naver_api_{start_date}_to_{end_date}.json'
        crawler.save_to_json(final_results, filename)
        
        # 통계
        print(f"\n{'='*60}")
        print(f"✅ 크롤링 완료!")
        print(f"   전체 수집: {len(all_results)}건")
        print(f"   중복 제거: {len(final_results)}건")
        print(f"   저장 위치: {filename}")
        print(f"{'='*60}")
        
        # 키워드별 통계
        keyword_stats = {}
        for result in final_results:
            kw = result['keyword']
            keyword_stats[kw] = keyword_stats.get(kw, 0) + 1
        
        print(f"\n📊 키워드별 통계 (상위 10개):")
        for kw, count in sorted(keyword_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   - {kw}: {count}건")
    
    except ValueError as e:
        print(f"\n❌ 오류: {e}")
        print(f"\n💡 .env 파일에 다음을 추가하세요:")
        print(f"   NAVER_CLIENT_ID=your_client_id")
        print(f"   NAVER_CLIENT_SECRET=your_client_secret")


if __name__ == "__main__":
    main()
