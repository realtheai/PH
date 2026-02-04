"""
고해상도 구글 이미지 검색 (Bing Image Search API 사용)
무료이고 더 큰 이미지를 제공합니다
"""
import requests
import json
from datetime import datetime
from typing import List, Dict
import time
import os
from pathlib import Path
from PIL import Image
import io

class HighResImageCrawler:
    def __init__(self, output_dir: str = 'data/images/phishing_hd'):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def search_bing_images(self, query: str, count: int = 50) -> List[Dict]:
        """Bing 이미지 검색 (무료, API 키 불필요)"""
        results = []
        
        print(f"\n🔍 Bing 이미지 검색: '{query}'")
        
        try:
            # Bing 이미지 검색
            url = "https://www.bing.com/images/search"
            params = {
                'q': query,
                'first': 1,
                'count': count,
                'qft': '+filterui:imagesize-large',  # 큰 이미지만
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # 간단한 정규식으로 이미지 URL 추출
            import re
            pattern = r'"murl":"(https?://[^"]+)"'
            urls = re.findall(pattern, response.text)
            
            # 중복 제거
            urls = list(set(urls))[:count]
            
            print(f"   발견: {len(urls)}개 URL")
            
            # 이미지 다운로드
            for i, img_url in enumerate(urls):
                if i >= count:
                    break
                
                try:
                    # 이미지 다운로드
                    img_response = requests.get(img_url, headers=self.headers, timeout=15)
                    img_response.raise_for_status()
                    
                    # PIL로 이미지 열기
                    img = Image.open(io.BytesIO(img_response.content))
                    width, height = img.size
                    
                    # 너무 작은 이미지 스킵 (최소 400px)
                    if width < 400 or height < 400:
                        print(f"   ⚠️  너무 작음: {width}x{height} (스킵)")
                        continue
                    
                    # 너무 큰 이미지는 리사이즈 (최대 1200px)
                    if width > 1200 or height > 1200:
                        img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
                        width, height = img.size
                    
                    # 파일명
                    filename = f"{query.replace(' ', '_')}_{i+1}.jpg"
                    filepath = os.path.join(self.output_dir, filename)
                    
                    # RGB로 변환 (RGBA 등을 처리)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # 저장
                    img.save(filepath, 'JPEG', quality=90)
                    
                    result = {
                        'query': query,
                        'image_url': img_url,
                        'local_path': filepath,
                        'filename': filename,
                        'width': width,
                        'height': height,
                        'crawled_at': datetime.now().isoformat()
                    }
                    
                    results.append(result)
                    print(f"   ✅ [{len(results)}] {width}x{height}px")
                    
                    if len(results) >= count:
                        break
                
                except Exception as e:
                    # 개별 이미지 실패는 무시
                    continue
                
                time.sleep(0.5)  # Rate limiting
            
            print(f"   완료: {len(results)}개 다운로드")
        
        except Exception as e:
            print(f"   ❌ 검색 실패: {e}")
        
        return results
    
    def run(self, keywords: List[str], images_per_keyword: int = 30) -> List[Dict]:
        """전체 크롤링 실행"""
        print(f"\n{'='*60}")
        print(f"🚀 고해상도 이미지 크롤링")
        print(f"   키워드: {len(keywords)}개")
        print(f"   이미지/키워드: {images_per_keyword}개")
        print(f"{'='*60}")
        
        all_results = []
        
        for idx, keyword in enumerate(keywords, 1):
            print(f"\n[{idx}/{len(keywords)}] 키워드: {keyword}")
            results = self.search_bing_images(keyword, count=images_per_keyword)
            all_results.extend(results)
            time.sleep(2)  # Rate limiting
        
        print(f"\n{'='*60}")
        print(f"✅ 크롤링 완료!")
        print(f"   총 다운로드: {len(all_results)}개")
        print(f"   저장 위치: {self.output_dir}/")
        
        # 해상도 통계
        if all_results:
            widths = [r['width'] for r in all_results]
            heights = [r['height'] for r in all_results]
            print(f"\n📊 해상도 통계:")
            print(f"   평균: {sum(widths)//len(widths)}x{sum(heights)//len(heights)}px")
            print(f"   최소: {min(widths)}x{min(heights)}px")
            print(f"   최대: {max(widths)}x{max(heights)}px")
        
        print(f"{'='*60}\n")
        
        return all_results

def main():
    crawler = HighResImageCrawler(output_dir='data/images/phishing_hd')
    
    # 핵심 키워드만 선택 (고품질 이미지 우선)
    keywords = [
        '스미싱 문자 캡처',
        '피싱 메시지 스크린샷',
        '보이스피싱 문자',
        '택배 스미싱 화면',
        '카톡 피싱 대화',
        '금융감독원 사칭',
        '가족 사칭 카톡',
        '경찰 사칭 문자',
        'phishing text message screenshot',
        'smishing SMS capture'
    ]
    
    results = crawler.run(keywords=keywords, images_per_keyword=50)
    
    # 메타데이터 저장
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    metadata_file = f'data/raw/google_images_hd_{timestamp}.json'
    
    os.makedirs('data/raw', exist_ok=True)
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"💾 메타데이터 저장: {metadata_file}")
    
    # 키워드별 통계
    print(f"\n📊 키워드별 통계:")
    keyword_stats = {}
    for result in results:
        kw = result['query']
        keyword_stats[kw] = keyword_stats.get(kw, 0) + 1
    
    for kw, count in sorted(keyword_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"   - {kw}: {count}개")

if __name__ == "__main__":
    main()
