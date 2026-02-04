"""
통합 크롤링 실행 스크립트 (2025-02-01 ~ 2026-01-31)
"""
import sys
from pathlib import Path
import time
from datetime import datetime

sys.path.append(str(Path(__file__).parent))

def main():
    start_time = datetime.now()
    
    print("="*70)
    print("🚀 피싱 데이터 수집 시작 (2025-02-01 ~ 2026-01-31)")
    print("="*70)
    
    crawlers = [
        ("네이버 API", "crawl_naver_api.py", "약 25분"),
        ("구글 뉴스", "crawl_google_news.py", "약 15분"),
        ("Reddit", "crawl_reddit.py", "약 5분"),
        ("해외 뉴스", "crawl_international_news.py", "약 3분"),
        ("구글 이미지", "crawl_google_images.py", "약 10분")
    ]
    
    print(f"\n📋 크롤링 계획:")
    for i, (name, script, duration) in enumerate(crawlers, 1):
        print(f"   {i}. {name} ({script}) - {duration}")
    
    print(f"\n⏱️ 예상 총 소요 시간: 약 60분")
    print(f"📦 예상 데이터 수집량: 약 5,000~7,000건")
    print(f"\n{'='*70}\n")
    
    # 사용자 확인
    user_input = input("크롤링을 시작하시겠습니까? (y/N): ")
    if user_input.lower() != 'y':
        print("\n❌ 크롤링이 취소되었습니다.")
        return
    
    print(f"\n{'='*70}")
    print(f"⚡ 크롤링 시작!")
    print(f"{'='*70}\n")
    
    # 각 크롤러 실행
    for i, (name, script, duration) in enumerate(crawlers, 1):
        print(f"\n{'='*70}")
        print(f"[{i}/{len(crawlers)}] {name} 크롤링 시작...")
        print(f"{'='*70}")
        
        import subprocess
        result = subprocess.run(
            ['python', f'scripts/{script}'],
            capture_output=False
        )
        
        if result.returncode != 0:
            print(f"\n⚠️ {name} 크롤링 실패")
        else:
            print(f"\n✅ {name} 크롤링 완료")
        
        # 다음 크롤러 시작 전 대기
        if i < len(crawlers):
            print(f"\n⏳ 3초 대기 후 다음 크롤러 시작...\n")
            time.sleep(3)
    
    # 완료
    end_time = datetime.now()
    elapsed = end_time - start_time
    
    print(f"\n{'='*70}")
    print(f"🎉 모든 크롤링 완료!")
    print(f"   총 소요 시간: {elapsed}")
    print(f"   저장 위치: data/raw/")
    print(f"{'='*70}\n")
    
    print(f"📂 수집된 파일:")
    print(f"   - naver_api_2025-02-01_to_2026-01-31.json")
    print(f"   - google_news_2025-02-01_to_2026-01-31.json")
    print(f"   - reddit_2025-02-01_to_2026-01-31.json")
    print(f"   - international_news_2025-02-01_to_2026-01-31.json")
    print(f"   - google_images_2025-02-01_to_2026-01-31.json")
    print(f"\n💡 다음 단계:")
    print(f"   1. 수집된 데이터 품질 확인")
    print(f"   2. 중복 제거 및 전처리")
    print(f"   3. Vector DB 구축")

if __name__ == "__main__":
    main()
