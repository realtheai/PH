"""
구글 이미지 검색 - 피싱/스미싱 사례 이미지 수집
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from typing import List, Dict
import time
import re
import os
from urllib.parse import quote
import base64

class GoogleImageCrawler:
    def __init__(self, output_dir: str = 'data/images'):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def search_images(self, query: str, max_images: int = 100) -> List[Dict]:
        """구글 이미지 검색"""
        results = []
        
        print(f"\n🔍 구글 이미지 검색: '{query}'")
        
        try:
            # 구글 이미지 검색 URL
            url = "https://www.google.com/search"
            params = {
                'q': query,
                'tbm': 'isch',  # 이미지 검색
                'hl': 'ko',
                'gl': 'kr'
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 이미지 URL 추출
            image_elements = soup.select('img')
            
            for i, img in enumerate(image_elements[:max_images]):
                try:
                    # 이미지 URL
                    img_url = img.get('src') or img.get('data-src')
                    
                    if not img_url or 'base64' in img_url:
                        continue
                    
                    # 이미지 다운로드
                    img_filename = f"{query.replace(' ', '_')}_{i+1}.jpg"
                    img_path = os.path.join(self.output_dir, img_filename)
                    
                    # 이미지 저장
                    if self._download_image(img_url, img_path):
                        result = {
                            'query': query,
                            'image_url': img_url,
                            'local_path': img_path,
                            'filename': img_filename,
                            'index': i + 1,
                            'crawled_at': datetime.now().isoformat()
                        }
                        results.append(result)
                
                except Exception as e:
                    continue
            
            print(f"   ✅ {len(results)}개 이미지 다운로드 완료")
            time.sleep(2)
        
        except Exception as e:
            print(f"   ❌ 검색 실패: {e}")
        
        return results
    
    def _download_image(self, url: str, filepath: str) -> bool:
        """이미지 다운로드"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            return True
        
        except Exception as e:
            return False
    
    def save_metadata(self, data: List[Dict], filename: str = None):
        """메타데이터 JSON 저장"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'data/raw/google_images_{timestamp}.json'
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 메타데이터 저장: {filename}")
    
    def run(self, keywords: List[str] = None, max_images_per_keyword: int = 50):
        """전체 크롤링 실행"""
        if keywords is None:
            keywords = [
                '스미싱 문자 사례',
                '피싱 메시지',
                '보이스피싱 수법',
                '금융사기 문자',
                '택배 스미싱',
                '카톡 피싱',
                '인터넷 사기',
                '금융감독원 사칭',
                'phishing message example',
                'smishing text example'
            ]
        
        print(f"\n{'='*60}")
        print(f"🚀 구글 이미지 크롤링 시작")
        print(f"   키워드: {len(keywords)}개")
        print(f"   이미지/키워드: 최대 {max_images_per_keyword}개")
        print(f"{'='*60}")
        
        all_results = []
        
        for keyword in keywords:
            results = self.search_images(keyword, max_images=max_images_per_keyword)
            all_results.extend(results)
            time.sleep(3)  # Rate limiting
        
        print(f"\n{'='*60}")
        print(f"✅ 크롤링 완료!")
        print(f"   총 다운로드: {len(all_results)}개 이미지")
        print(f"   저장 위치: {self.output_dir}/")
        print(f"{'='*60}\n")
        
        return all_results


def main():
    crawler = GoogleImageCrawler(output_dir='data/images/phishing')
    
    # 한국어 + 영어 키워드 (최신 수법 포함)
    keywords = [
        '스미싱 문자 사례',
        '피싱 메시지 예시',
        '보이스피싱 수법',
        '금융사기 문자',
        '택배 스미싱 사례',
        '카톡 피싱 캡처',
        '메신저 피싱 대화',
        '금융감독원 사칭 문자',
        '공공기관 사칭 메시지',
        '인터넷 사기 문자',
        '부고 문자 캡처',
        '청첩장 스미싱 화면',
        '가족 사칭 카톡 예시',
        '결제 알림 피싱 문자',
        'phishing message example',
        'smishing text screenshot',
        'scam message example',
        'fraud text message',
        'WhatsApp scam screenshot',
        'Telegram phishing capture'
    ]
    
    results = crawler.run(keywords=keywords, max_images_per_keyword=50)
    
    # 메타데이터 저장
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    crawler.save_metadata(results, f'data/raw/google_images_{timestamp}.json')
    
    print("\n📊 수집 통계:")
    print(f"   총 이미지: {len(results)}개")
    
    # 키워드별 통계
    keyword_stats = {}
    for result in results:
        kw = result['query']
        keyword_stats[kw] = keyword_stats.get(kw, 0) + 1
    
    print(f"\n   키워드별:")
    for kw, count in sorted(keyword_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"      - {kw}: {count}개")


if __name__ == "__main__":
    main()
