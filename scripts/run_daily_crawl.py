"""
매일 전체 크롤링 실행 스크립트
"""
import sys
from pathlib import Path
import time
from datetime import datetime

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    print("="*70)
    print(f"🤖 매일 자동 크롤링 시작 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    print("="*70)
    
    crawlers = [
        {'name': '네이버 뉴스', 'module': 'daily_naver', 'emoji': '📰'},
        {'name': '구글 뉴스', 'module': 'daily_google', 'emoji': '🌐'},
        {'name': '구글 이미지', 'module': 'daily_google_images', 'emoji': '🖼️'},
        {'name': 'Reddit', 'module': 'daily_reddit', 'emoji': '🔴'},
        {'name': '해외 뉴스', 'module': 'daily_international', 'emoji': '🌍'},
    ]
    
    results = {}
    
    for idx, crawler in enumerate(crawlers, 1):
        print(f"\n{'='*70}")
        print(f"{crawler['emoji']} [{idx}/{len(crawlers)}] {crawler['name']} 크롤링 시작")
        print(f"{'='*70}")
        
        start_time = time.time()
        
        try:
            # 동적 import
            module = __import__(f"scripts.{crawler['module']}", fromlist=['daily_update'])
            result = module.daily_update()
            
            elapsed = time.time() - start_time
            results[crawler['name']] = {
                'status': 'success',
                'count': len(result) if result else 0,
                'time': f"{elapsed:.1f}초"
            }
            
            print(f"\n✅ {crawler['name']} 완료 ({elapsed:.1f}초)")
            
        except Exception as e:
            elapsed = time.time() - start_time
            results[crawler['name']] = {
                'status': 'failed',
                'error': str(e),
                'time': f"{elapsed:.1f}초"
            }
            print(f"\n❌ {crawler['name']} 실패: {e}")
        
        # 다음 크롤러 전 잠시 대기
        if idx < len(crawlers):
            time.sleep(2)
    
    # 최종 요약
    print("\n" + "="*70)
    print("📊 크롤링 결과 요약")
    print("="*70)
    
    total_count = 0
    success_count = 0
    
    for name, result in results.items():
        status_emoji = "✅" if result['status'] == 'success' else "❌"
        count_str = f"{result['count']}건" if 'count' in result else "실패"
        print(f"{status_emoji} {name:15} - {count_str:10} ({result['time']})")
        
        if result['status'] == 'success':
            success_count += 1
            total_count += result.get('count', 0)
    
    print(f"\n{'='*70}")
    print(f"🎉 전체 완료: {success_count}/{len(crawlers)} 성공")
    print(f"📦 총 수집: {total_count}건")
    print(f"⏱️  완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")
    
    print(f"\n📋 다음 단계:")
    print(f"   1. 데이터 정제: python scripts/auto_process_and_upload.py")
    print(f"   2. DB 업로드: 자동 실행됨")

if __name__ == "__main__":
    main()
