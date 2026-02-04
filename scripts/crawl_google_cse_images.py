"""
Google Custom Search API로 고해상도 이미지 수집
"""
import os
import requests
import json
from datetime import datetime
from typing import List, Dict
import time
from pathlib import Path
from PIL import Image
import io
from dotenv import load_dotenv

load_dotenv()

class GoogleCSEImageCrawler:
    def __init__(self, api_key: str, cx: str, output_dir: str = 'data/images/phishing_hd'):
        self.api_key = api_key
        self.cx = cx
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def search_images(self, query: str, num_images: int = 10) -> List[Dict]:
        """Google Custom Search API로 이미지 검색"""
        results = []
        
        print(f"\n🔍 Google CSE 이미지 검색: '{query}'")
        
        # API는 한 번에 최대 10개씩만 가능
        total_fetched = 0
        start_index = 1
        
        while total_fetched < num_images:
            try:
                url = "https://www.googleapis.com/customsearch/v1"
                params = {
                    'key': self.api_key,
                    'cx': self.cx,
                    'q': query,
                    'searchType': 'image',
                    'num': min(10, num_images - total_fetched),
                    'start': start_index,
                    'imgSize': 'large',  # 큰 이미지만
                    'safe': 'off',
                    'gl': 'kr',
                    'hl': 'ko'
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 403:
                    print(f"   ⚠️  API 쿼터 초과 또는 권한 없음")
                    break
                
                response.raise_for_status()
                data = response.json()
                
                if 'items' not in data:
                    print(f"   ⚠️  검색 결과 없음")
                    break
                
                items = data['items']
                print(f"   발견: {len(items)}개 이미지")
                
                # 각 이미지 다운로드
                for idx, item in enumerate(items):
                    try:
                        img_url = item['link']
                        
                        # 이미지 다운로드
                        img_response = requests.get(img_url, timeout=15)
                        img_response.raise_for_status()
                        
                        # PIL로 검증 및 리사이즈
                        img = Image.open(io.BytesIO(img_response.content))
                        width, height = img.size
                        
                        # 너무 작은 이미지 스킵
                        if width < 400 or height < 400:
                            print(f"   ⚠️  [{total_fetched + idx + 1}] 너무 작음: {width}x{height} (스킵)")
                            continue
                        
                        # 너무 큰 이미지는 리사이즈
                        if width > 1200 or height > 1200:
                            img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
                            width, height = img.size
                        
                        # 파일명
                        filename = f"{query.replace(' ', '_')}_{total_fetched + idx + 1}.jpg"
                        filepath = os.path.join(self.output_dir, filename)
                        
                        # RGB 변환
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        
                        # 저장
                        img.save(filepath, 'JPEG', quality=95)
                        
                        result = {
                            'query': query,
                            'image_url': img_url,
                            'local_path': filepath,
                            'filename': filename,
                            'width': width,
                            'height': height,
                            'title': item.get('title', ''),
                            'source': item.get('displayLink', ''),
                            'crawled_at': datetime.now().isoformat()
                        }
                        
                        results.append(result)
                        print(f"   ✅ [{len(results)}] {width}x{height}px - {item.get('title', '')[:30]}")
                    
                    except Exception as e:
                        continue
                
                total_fetched += len(items)
                start_index += 10
                
                # API Rate Limit
                time.sleep(1)
            
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    print(f"   ⚠️  Rate limit - 대기 중...")
                    time.sleep(5)
                else:
                    print(f"   ❌ HTTP 에러: {e}")
                    break
            except Exception as e:
                print(f"   ❌ 검색 실패: {e}")
                break
        
        print(f"   완료: {len(results)}개 다운로드")
        return results
    
    def run(self, keywords: List[str], images_per_keyword: int = 30) -> List[Dict]:
        """전체 크롤링 실행"""
        print(f"\n{'='*60}")
        print(f"🚀 Google CSE 고해상도 이미지 크롤링")
        print(f"   키워드: {len(keywords)}개")
        print(f"   이미지/키워드: {images_per_keyword}개")
        print(f"{'='*60}")
        
        all_results = []
        total_queries = 0
        
        for idx, keyword in enumerate(keywords, 1):
            print(f"\n[{idx}/{len(keywords)}] 키워드: {keyword}")
            results = self.search_images(keyword, num_images=images_per_keyword)
            all_results.extend(results)
            total_queries += (images_per_keyword + 9) // 10  # 10개씩 나눠서 계산
            time.sleep(2)
        
        print(f"\n{'='*60}")
        print(f"✅ 크롤링 완료!")
        print(f"   총 다운로드: {len(all_results)}개")
        print(f"   API 쿼리 사용: ~{total_queries}회")
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
    api_key = os.getenv('GOOGLE_SAFE_BROWSING_API_KEY')
    cx = os.getenv('GOOGLE_CSE_CX')
    
    if not api_key or not cx:
        print("❌ GOOGLE_SAFE_BROWSING_API_KEY 또는 GOOGLE_CSE_CX가 .env에 없습니다!")
        return
    
    crawler = GoogleCSEImageCrawler(api_key=api_key, cx=cx, output_dir='data/images/phishing_hd')
    
    # 핵심 키워드 (고품질 우선)
    keywords = [
        '스미싱 문자 캡처',
        '피싱 메시지 스크린샷',
        '보이스피싱 문자',
        '택배 스미싱 화면',
        '카톡 피싱 대화',
        '금융감독원 사칭 문자',
        '가족 사칭 카톡',
        '경찰청 사칭 문자',
        'phishing text message screenshot',
        'smishing SMS screenshot'
    ]
    
    results = crawler.run(keywords=keywords, images_per_keyword=40)
    
    # 메타데이터 저장
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    metadata_file = f'data/raw/google_cse_images_{timestamp}.json'
    
    os.makedirs('data/raw', exist_ok=True)
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"💾 메타데이터 저장: {metadata_file}")
    
    # 키워드별 통계
    if results:
        print(f"\n📊 키워드별 통계:")
        keyword_stats = {}
        for result in results:
            kw = result['query']
            keyword_stats[kw] = keyword_stats.get(kw, 0) + 1
        
        for kw, count in sorted(keyword_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"   - {kw}: {count}개")

if __name__ == "__main__":
    main()
