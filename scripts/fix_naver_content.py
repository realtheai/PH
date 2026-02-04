"""
네이버 뉴스 전용 파서 - 본문 추출 실패 데이터 복구
"""
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from typing import Dict
import time

class NaverNewsParser:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def parse_naver_news(self, url: str) -> str:
        """네이버 뉴스 본문 추출 (BeautifulSoup + 네이버 셀렉터)"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 네이버 뉴스 본문 셀렉터 (우선순위 순)
            selectors = [
                '#dic_area',           # 일반 네이버 뉴스
                '#articeBody',         # 구형 네이버 뉴스
                '.article_body',       # 언론사 직접 게재
                '#articleBodyContents', # 또 다른 형식
                '.news_end',           # 예전 형식
            ]
            
            article_text = ""
            
            for selector in selectors:
                article = soup.select_one(selector)
                if article:
                    # 스크립트, 광고 등 제거
                    for tag in article.find_all(['script', 'style', 'iframe', 'ins']):
                        tag.decompose()
                    
                    # 텍스트 추출
                    article_text = article.get_text(separator='\n', strip=True)
                    
                    # 최소 길이 확인
                    if len(article_text) >= 300:
                        break
            
            # 공백 정리
            article_text = '\n'.join(line.strip() for line in article_text.split('\n') if line.strip())
            
            return article_text
        
        except Exception as e:
            print(f"      ⚠️ 파싱 실패: {e}")
            return ""
    
    def reparse_short_articles(self, input_file: str, output_file: str, min_length: int = 200):
        """짧은 본문 데이터 재파싱"""
        print(f"\n{'='*60}")
        print(f"🔧 네이버 뉴스 재크롤링 시작")
        print(f"{'='*60}")
        
        # 원본 데이터 로드
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 짧은 데이터 필터링
        short_articles = [d for d in data if d['content_length'] < min_length]
        good_articles = [d for d in data if d['content_length'] >= min_length]
        
        print(f"\n📊 분석 결과:")
        print(f"   전체: {len(data)}건")
        print(f"   양호: {len(good_articles)}건 (유지)")
        print(f"   재크롤링 대상: {len(short_articles)}건")
        print(f"\n{'='*60}\n")
        
        # 재크롤링
        recovered = 0
        failed = 0
        
        for idx, article in enumerate(short_articles, 1):
            url = article['url']
            print(f"[{idx}/{len(short_articles)}] 재파싱 중...", end=' ')
            
            new_content = self.parse_naver_news(url)
            
            if new_content and len(new_content) >= 300:
                article['content'] = new_content
                article['content_length'] = len(new_content)
                article['reparsed_at'] = datetime.now().isoformat()
                recovered += 1
                print(f"✅ ({len(new_content)}자)")
            else:
                failed += 1
                print(f"❌ (실패)")
            
            time.sleep(0.3)  # 서버 부하 방지
        
        # 데이터 병합
        final_data = good_articles + short_articles
        
        # 저장
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n{'='*60}")
        print(f"✅ 재크롤링 완료!")
        print(f"   복구 성공: {recovered}건")
        print(f"   복구 실패: {failed}건")
        print(f"   최종 저장: {output_file}")
        print(f"{'='*60}\n")
        
        # 최종 통계
        final_good = [d for d in final_data if d['content_length'] >= 500]
        print(f"📊 최종 품질:")
        print(f"   전체: {len(final_data)}건")
        print(f"   양호 (500자+): {len(final_good)}건 ({len(final_good)/len(final_data)*100:.1f}%)")
        
        return final_data

def main():
    parser = NaverNewsParser()
    
    input_file = 'data/raw/naver_api_2025-02-01_to_2026-01-31.json'
    output_file = 'data/raw/naver_api_2025-02-01_to_2026-01-31_fixed.json'
    
    parser.reparse_short_articles(input_file, output_file, min_length=200)

if __name__ == "__main__":
    main()
