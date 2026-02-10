"""
벡터 검색 모듈 (클라이언트 측 계산, RPC timeout 회피)
"""
import os
import requests
import json
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')

class VectorSearcher:
    """벡터 검색 클래스 (RPC 우회, 직접 계산)"""
    
    def __init__(self):
        """초기화"""
        self.supabase_url = SUPABASE_URL
        self.supabase_key = SUPABASE_KEY
        self.headers = {
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json'
        }
        print("✅ VectorSearcher 초기화: 클라이언트 측 계산 방식")
    
    def calculate_similarity(self, query_embedding: List[float], item_embedding) -> float:
        """
        코사인 유사도 계산
        
        Args:
            query_embedding: 쿼리 임베딩 벡터
            item_embedding: DB 아이템 임베딩 (문자열 또는 리스트)
        
        Returns:
            코사인 유사도 (0~1)
        """
        try:
            # 문자열인 경우 JSON 파싱
            if isinstance(item_embedding, str):
                item_embedding = json.loads(item_embedding)
            
            # 리스트가 아니면 실패
            if not isinstance(item_embedding, list):
                return 0.0
            
            # 차원이 다르면 실패
            if len(query_embedding) != len(item_embedding):
                return 0.0
            
            # 코사인 유사도 계산 (numpy 없이)
            dot_product = sum(q * i for q, i in zip(query_embedding, item_embedding))
            query_norm = sum(q * q for q in query_embedding) ** 0.5
            item_norm = sum(i * i for i in item_embedding) ** 0.5
            
            if query_norm == 0 or item_norm == 0:
                return 0.0
            
            cosine_sim = dot_product / (query_norm * item_norm)
            return max(0.0, min(1.0, cosine_sim))  # 0~1 범위로 클리핑
            
        except Exception as e:
            return 0.0
    
    def fetch_news(self, limit: int = 100) -> List[Dict]:
        """
        뉴스 데이터 조회
        
        Args:
            limit: 조회할 최대 개수
        
        Returns:
            뉴스 리스트
        """
        try:
            url = f"{self.supabase_url}/rest/v1/phishing_news"
            params = {
                'select': 'id,title,content,translated_content,source,phishing_type,classification,embedding',
                'classification': 'in.(REAL_CASE,NEWS)',
                'embedding': 'not.is.null',
                'limit': str(limit)
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"⚠️  뉴스 조회 실패: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ 뉴스 조회 오류: {e}")
            return []
    
    def fetch_images(self, limit: int = 100) -> List[Dict]:
        """
        이미지 데이터 조회
        
        Args:
            limit: 조회할 최대 개수
        
        Returns:
            이미지 리스트
        """
        try:
            url = f"{self.supabase_url}/rest/v1/phishing_images"
            params = {
                'select': 'id,ocr_text,translated_text,translated_content,source,phishing_type,classification,embedding',
                'classification': 'in.(REAL_CASE,NEWS)',
                'embedding': 'not.is.null',
                'limit': str(limit)
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"⚠️  이미지 조회 실패: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ 이미지 조회 오류: {e}")
            return []
    
    def search_similar_cases(
        self, 
        query_embedding: List[float], 
        threshold: float = 0.3, 
        limit: int = 5,
        max_fetch: int = 300
    ) -> List[Dict]:
        """
        유사 피싱 사례 검색 (클라이언트 측 계산)
        
        Args:
            query_embedding: 쿼리 임베딩 벡터
            threshold: 최소 유사도 임계값 (0~1)
            limit: 반환할 최대 결과 개수
            max_fetch: DB에서 가져올 최대 데이터 개수
        
        Returns:
            유사 사례 리스트 (유사도 높은 순)
        """
        try:
            print(f"🔍 Vector Search 시작 (클라이언트 측 계산)")
            
            # 1. 데이터 조회
            news_items = self.fetch_news(limit=max_fetch)
            image_items = self.fetch_images(limit=max_fetch)
            print(f"   데이터 조회: 뉴스 {len(news_items)}개, 이미지 {len(image_items)}개")
            
            # 2. 유사도 계산
            results = []
            
            # 뉴스 처리
            for item in news_items:
                if item.get('embedding'):
                    similarity = self.calculate_similarity(query_embedding, item['embedding'])
                    if similarity > threshold:
                        results.append({
                            'id': item['id'],
                            'source_type': 'news',
                            'title': item.get('title'),
                            'content': item.get('translated_content') or item.get('content'),
                            'source': item.get('source'),
                            'phishing_type': item.get('phishing_type'),
                            'similarity': similarity
                        })
            
            # 이미지 처리
            for item in image_items:
                if item.get('embedding'):
                    similarity = self.calculate_similarity(query_embedding, item['embedding'])
                    if similarity > threshold:
                        results.append({
                            'id': item['id'],
                            'source_type': 'image',
                            'title': None,
                            'content': (
                                item.get('translated_content') or 
                                item.get('translated_text') or 
                                item.get('ocr_text')
                            ),
                            'source': item.get('source'),
                            'phishing_type': item.get('phishing_type'),
                            'similarity': similarity
                        })
            
            # 3. 유사도 기준 정렬
            results.sort(key=lambda x: x['similarity'], reverse=True)
            
            # 4. 상위 N개만 반환
            top_results = results[:limit]
            
            print(f"✅ Vector Search 완료: {len(top_results)}건 발견 (전체 {len(results)}건 중)")
            
            return top_results
            
        except Exception as e:
            print(f"❌ Vector Search 오류: {e}")
            import traceback
            traceback.print_exc()
            return []
