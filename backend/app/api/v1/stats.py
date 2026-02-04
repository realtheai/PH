"""
통계 API 엔드포인트
"""
from fastapi import APIRouter, HTTPException
from app.schemas.request import StatsResponse
import os
import requests

router = APIRouter()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """
    통계 조회 엔드포인트
    
    - 전체 뉴스/이미지 수
    - 최근 피싱 유형 분포
    - 일별 통계
    """
    try:
        # 전체 뉴스 수 (REST API)
        news_url = f"{SUPABASE_URL}/rest/v1/phishing_news"
        news_response = requests.get(
            news_url,
            headers={**HEADERS, 'Prefer': 'count=exact'},
            params={'select': 'id', 'limit': 0},
            timeout=10
        )
        total_news = int(news_response.headers.get('Content-Range', '0').split('/')[-1])
        
        # 전체 이미지 수
        images_url = f"{SUPABASE_URL}/rest/v1/phishing_images"
        images_response = requests.get(
            images_url,
            headers={**HEADERS, 'Prefer': 'count=exact'},
            params={'select': 'id', 'limit': 0},
            timeout=10
        )
        total_images = int(images_response.headers.get('Content-Range', '0').split('/')[-1])
        
        # 최근 피싱 유형 분포
        category_response = requests.get(
            news_url,
            headers=HEADERS,
            params={'select': 'category', 'limit': 1000},
            timeout=10
        )
        category_data = category_response.json()
        
        category_distribution = {}
        for item in category_data:
            cat = item.get('category', 'UNKNOWN')
            category_distribution[cat] = category_distribution.get(cat, 0) + 1
        
        recent_types = [
            {'type': k, 'count': v} 
            for k, v in category_distribution.items()
        ]
        
        # 일별 통계
        stats_url = f"{SUPABASE_URL}/rest/v1/phishing_stats"
        stats_response = requests.get(
            stats_url,
            headers=HEADERS,
            params={'select': '*', 'order': 'stat_date.desc', 'limit': 7},
            timeout=10
        )
        daily_stats = stats_response.json()
        
        return StatsResponse(
            total_news=total_news,
            total_images=total_images,
            recent_phishing_types=recent_types,
            daily_stats=daily_stats
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}")
