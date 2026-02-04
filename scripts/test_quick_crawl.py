"""
간단한 크롤링 테스트 (1개 키워드만)
"""
from crawl_naver_api import NaverAPINewsCrawler
from datetime import datetime

def quick_test():
    print("="*60)
    print("🧪 네이버 API 크롤링 테스트")
    print("="*60)
    
    crawler = NaverAPINewsCrawler()
    
    # 1개 키워드만 테스트
    keyword = '보이스피싱'
    print(f"\n테스트 키워드: {keyword}")
    
    results = crawler.search_news(keyword, display=10, start=1)
    
    print(f"\n✅ 수집 완료: {len(results)}건")
    
    if results:
        print(f"\n📄 첫 번째 결과:")
        first = results[0]
        print(f"   제목: {first['title'][:50]}...")
        print(f"   URL: {first['url']}")
        print(f"   본문 길이: {first['content_length']}자")
        print(f"   키워드: {first.get('keywords', [])}")
    
    return results

if __name__ == "__main__":
    quick_test()
