"""
통계 API 엔드포인트
"""
from fastapi import APIRouter, HTTPException
from app.schemas.request import StatsResponse
from app.storage.supabase import get_supabase

router = APIRouter()

@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """
    통계 조회 엔드포인트
    
    - 전체 뉴스/이미지 수
    - 최근 피싱 유형 분포
    - 일별 통계
    """
    try:
        supabase = get_supabase()
        
        # 전체 뉴스 수
        news_count = supabase.table('phishing_news').select('id', count='exact').execute()
        total_news = news_count.count if news_count else 0
        
        # 전체 이미지 수
        images_count = supabase.table('phishing_images').select('id', count='exact').execute()
        total_images = images_count.count if images_count else 0
        
        # 최근 피싱 유형 분포 (카테고리별)
        category_stats = supabase.table('phishing_news')\
            .select('category')\
            .limit(1000)\
            .execute()
        
        category_distribution = {}
        if category_stats.data:
            for item in category_stats.data:
                cat = item.get('category', 'UNKNOWN')
                category_distribution[cat] = category_distribution.get(cat, 0) + 1
        
        recent_types = [
            {'type': k, 'count': v} 
            for k, v in category_distribution.items()
        ]
        
        # 일별 통계 (최근 7일)
        daily_stats_data = supabase.table('phishing_stats')\
            .select('*')\
            .order('stat_date', desc=True)\
            .limit(7)\
            .execute()
        
        daily_stats = daily_stats_data.data if daily_stats_data.data else []
        
        return StatsResponse(
            total_news=total_news,
            total_images=total_images,
            recent_phishing_types=recent_types,
            daily_stats=daily_stats
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}")
