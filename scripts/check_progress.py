"""
임베딩 진행 상황 확인
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
}

def check_progress():
    """진행 상황 확인"""
    url = f"{SUPABASE_URL}/rest/v1/phishing_embedding_stats"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data:
            stats = data[0]
            total = stats.get('total_records', 0)
            completed = stats.get('embedded_records', 0)
            pending = stats.get('pending_records', 0)
            percentage = stats.get('completion_percentage', 0)
            
            print("=" * 60)
            print("📊 임베딩 진행 상황")
            print("=" * 60)
            print(f"총 레코드:    {total:,}건")
            print(f"완료:         {completed:,}건")
            print(f"대기 중:      {pending:,}건")
            print(f"진행률:       {percentage}%")
            print("=" * 60)
            
            # 프로그레스 바
            bar_length = 50
            filled = int(bar_length * percentage / 100)
            bar = '█' * filled + '░' * (bar_length - filled)
            print(f"[{bar}] {percentage}%")
            
            # 예상 남은 시간
            if pending > 0:
                remaining_time = pending * 0.5 / 60  # 분 단위
                print(f"\n예상 남은 시간: {remaining_time:.1f}분")
        else:
            print("통계 조회 실패")
            
    except Exception as e:
        print(f"오류: {e}")


if __name__ == "__main__":
    check_progress()
