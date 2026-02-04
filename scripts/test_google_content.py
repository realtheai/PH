"""
Google News + newspaper3k 본문 추출 테스트 스크립트
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.crawl_google_news import GoogleNewsCrawler

def test_google_full_content():
    print("="*60)
    print("🧪 구글 뉴스 + newspaper3k 본문 추출 테스트")
    print("="*60)
    
    crawler = GoogleNewsCrawler()
    
    # 1개 키워드만 테스트
    results = crawler.search_news('피싱 사례', max_results=3)
    
    print(f"\n{'='*60}")
    print(f"✅ 테스트 완료: {len(results)}건 수집")
    print(f"{'='*60}\n")
    
    # 결과 샘플 출력
    for i, result in enumerate(results, 1):
        print(f"\n[{i}] {result['title']}")
        print(f"    URL: {result['url'][:80]}...")
        print(f"    본문 길이: {result.get('content_length', 0)}자")
        print(f"    본문 미리보기: {result['content'][:200]}...")
        print(f"    키워드: {', '.join(result['extracted_keywords'][:5])}")
    
    return results

if __name__ == "__main__":
    test_google_full_content()
