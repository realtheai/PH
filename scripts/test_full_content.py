"""
newspaper3k 본문 추출 테스트 스크립트
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.crawl_naver_api import NaverAPINewsCrawler

def test_naver_full_content():
    print("="*60)
    print("🧪 네이버 API + newspaper3k 본문 추출 테스트")
    print("="*60)
    
    crawler = NaverAPINewsCrawler()
    
    # 1개 키워드만 테스트 (피싱 주의보)
    results = crawler.search_news('피싱 주의보', display=3)
    
    print(f"\n{'='*60}")
    print(f"✅ 테스트 완료: {len(results)}건 수집")
    print(f"{'='*60}\n")
    
    # 결과 샘플 출력
    for i, result in enumerate(results, 1):
        print(f"\n[{i}] {result['title']}")
        print(f"    URL: {result['url'][:80]}...")
        print(f"    본문 길이: {result['content_length']}자")
        print(f"    본문 미리보기: {result['content'][:200]}...")
        print(f"    키워드: {', '.join(result['extracted_keywords'][:5])}")
    
    return results

if __name__ == "__main__":
    test_naver_full_content()
