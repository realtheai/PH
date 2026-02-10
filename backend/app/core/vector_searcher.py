"""
벡터 검색 모듈 (Supabase pgvector RPC)
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
    """벡터 검색 클래스 (Supabase pgvector + HNSW 인덱스)"""
    
    def __init__(self):
        """초기화"""
        self.supabase_url = SUPABASE_URL
        self.supabase_key = SUPABASE_KEY
        self.headers = {
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json'
        }
        print("✅ VectorSearcher 초기화: pgvector RPC 방식 (전체 DB 검색)")
    
    def search_news_by_vector(
        self, 
        query_embedding: List[float], 
        threshold: float = 0.3, 
        limit: int = 3
    ) -> List[Dict]:
        """
        뉴스 벡터 검색 (pgvector RPC)
        네이버, 구글, Reddit 뉴스 5,800개 전체 검색
        
        Args:
            query_embedding: 쿼리 임베딩 벡터
            threshold: 최소 유사도 (0~1)
            limit: 반환 개수
        
        Returns:
            유사 뉴스 리스트
        """
        try:
            url = f"{self.supabase_url}/rest/v1/rpc/find_similar_phishing"
            
            # vector 타입으로 변환 (PostgreSQL vector 형식: [1,2,3,...])
            vector_string = json.dumps(query_embedding)
            
            payload = {
                'query_embedding': vector_string,  # JSON 문자열로 전송
                'match_threshold': threshold,
                'match_count': limit
            }
            
            response = requests.post(
                url, 
                headers=self.headers, 
                json=payload, 
                timeout=60
            )
            
            if response.status_code == 200:
                results = response.json()
                return [
                    {
                        'id': item['id'],
                        'source_type': 'news',
                        'title': item.get('title'),
                        'content': item.get('content'),
                        'source': item.get('source'),
                        'phishing_type': item.get('phishing_type'),
                        'similarity': item.get('similarity', 0)
                    }
                    for item in results
                ]
            else:
                print(f"⚠️  뉴스 벡터 검색 실패: {response.status_code}")
                print(f"   응답: {response.text[:200]}")
                # Fallback: 클라이언트 방식으로 전환
                print(f"   🔄 Fallback: 클라이언트 방식으로 전환")
                return self._search_news_client_side(query_embedding, threshold, limit)
                
        except Exception as e:
            print(f"❌ 뉴스 벡터 검색 오류: {e}")
            # Fallback: 클라이언트 방식으로 전환
            print(f"   🔄 Fallback: 클라이언트 방식으로 전환")
            return self._search_news_client_side(query_embedding, threshold, limit)
    
    def search_images_by_vector(
        self, 
        query_embedding: List[float], 
        threshold: float = 0.3, 
        limit: int = 2
    ) -> List[Dict]:
        """
        이미지 벡터 검색 (pgvector RPC)
        Google Images OCR 1,337개 전체 검색
        
        Args:
            query_embedding: 쿼리 임베딩 벡터
            threshold: 최소 유사도 (0~1)
            limit: 반환 개수
        
        Returns:
            유사 이미지 리스트
        """
        try:
            url = f"{self.supabase_url}/rest/v1/rpc/find_similar_phishing_images"
            
            # vector 타입으로 변환 (PostgreSQL vector 형식: [1,2,3,...])
            vector_string = json.dumps(query_embedding)
            
            payload = {
                'query_embedding': vector_string,  # JSON 문자열로 전송
                'match_threshold': threshold,
                'match_count': limit
            }
            
            response = requests.post(
                url, 
                headers=self.headers, 
                json=payload, 
                timeout=60
            )
            
            if response.status_code == 200:
                results = response.json()
                return [
                    {
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
                        'similarity': item.get('similarity', 0)
                    }
                    for item in results
                ]
            else:
                print(f"⚠️  이미지 벡터 검색 실패: {response.status_code}")
                print(f"   응답: {response.text[:200]}")
                # Fallback: 클라이언트 방식으로 전환
                print(f"   🔄 Fallback: 클라이언트 방식으로 전환")
                return self._search_images_client_side(query_embedding, threshold, limit)
                
        except Exception as e:
            print(f"❌ 이미지 벡터 검색 오류: {e}")
            # Fallback: 클라이언트 방식으로 전환
            print(f"   🔄 Fallback: 클라이언트 방식으로 전환")
            return self._search_images_client_side(query_embedding, threshold, limit)
    
    def _search_news_client_side(
        self, 
        query_embedding: List[float], 
        threshold: float = 0.5, 
        limit: int = 3
    ) -> List[Dict]:
        """
        뉴스 벡터 검색 (클라이언트 방식 fallback)
        
        Args:
            query_embedding: 쿼리 임베딩
            threshold: 최소 유사도
            limit: 반환 개수
        
        Returns:
            유사 뉴스 리스트
        """
        try:
            url = f"{self.supabase_url}/rest/v1/phishing_news"
            params = {
                'select': 'id,title,content,source,phishing_type,embedding',
                'classification': 'in.(REAL_CASE,NEWS)',
                'embedding': 'not.is.null',
                'limit': '1000'  # 1000개 샘플링
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                items = response.json()
                results = []
                
                for item in items:
                    if item.get('embedding'):
                        similarity = self._calculate_similarity(query_embedding, item['embedding'])
                        if similarity > threshold:
                            results.append({
                                'id': item['id'],
                                'source_type': 'news',
                                'title': item.get('title'),
                                'content': item.get('content'),
                                'source': item.get('source'),
                                'phishing_type': item.get('phishing_type'),
                                'similarity': similarity
                            })
                
                results.sort(key=lambda x: x['similarity'], reverse=True)
                return results[:limit]
            else:
                return []
                
        except Exception as e:
            print(f"❌ 클라이언트 방식 뉴스 검색 오류: {e}")
            return []
    
    def _search_images_client_side(
        self, 
        query_embedding: List[float], 
        threshold: float = 0.3, 
        limit: int = 2
    ) -> List[Dict]:
        """
        이미지 벡터 검색 (클라이언트 방식 fallback)
        
        Args:
            query_embedding: 쿼리 임베딩
            threshold: 최소 유사도
            limit: 반환 개수
        
        Returns:
            유사 이미지 리스트
        """
        try:
            url = f"{self.supabase_url}/rest/v1/phishing_images"
            params = {
                'select': 'id,ocr_text,translated_text,translated_content,source,phishing_type,embedding',
                'classification': 'in.(REAL_CASE,NEWS)',
                'embedding': 'not.is.null',
                'limit': '500'  # 500개 샘플링
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                items = response.json()
                results = []
                
                for item in items:
                    if item.get('embedding'):
                        similarity = self._calculate_similarity(query_embedding, item['embedding'])
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
                
                results.sort(key=lambda x: x['similarity'], reverse=True)
                return results[:limit]
            else:
                return []
                
        except Exception as e:
            print(f"❌ 클라이언트 방식 이미지 검색 오류: {e}")
            return []
    
    def _calculate_similarity(self, query_embedding: List[float], item_embedding) -> float:
        """
        코사인 유사도 계산 (내부용)
        
        Args:
            query_embedding: 쿼리 임베딩
            item_embedding: 아이템 임베딩
        
        Returns:
            유사도 (0~1)
        """
        try:
            if isinstance(item_embedding, str):
                item_embedding = json.loads(item_embedding)
            
            if not isinstance(item_embedding, list) or len(query_embedding) != len(item_embedding):
                return 0.0
            
            dot_product = sum(q * i for q, i in zip(query_embedding, item_embedding))
            query_norm = sum(q * q for q in query_embedding) ** 0.5
            item_norm = sum(i * i for i in item_embedding) ** 0.5
            
            if query_norm == 0 or item_norm == 0:
                return 0.0
            
            return max(0.0, min(1.0, dot_product / (query_norm * item_norm)))
            
        except Exception as e:
            return 0.0
    
    def search_similar_cases(
        self, 
        query_embedding: List[float], 
        threshold: float = 0.3, 
        limit: int = 5
    ) -> List[Dict]:
        """
        유사 피싱 사례 검색 (pgvector RPC + HNSW 인덱스)
        
        Args:
            query_embedding: 쿼리 임베딩 벡터
            threshold: 최소 유사도 임계값 (0~1)
            limit: 반환할 최대 결과 개수
        
        Returns:
            유사 사례 리스트 (유사도 높은 순)
        """
        try:
            print(f"🔍 Vector Search 시작 (pgvector RPC - 전체 DB 검색)")
            
            # 1. 뉴스 검색 (pgvector RPC)
            news_limit = max(3, limit - 2)  # 뉴스 우선 (3~N개)
            news_results = self.search_news_by_vector(
                query_embedding=query_embedding,
                threshold=threshold,
                limit=news_limit
            )
            print(f"   뉴스 검색 (네이버/구글/Reddit): {len(news_results)}건 발견 (전체 5,800개 중)")
            
            # 2. 이미지 검색 (pgvector RPC)
            image_limit = min(2, limit)  # 이미지 보조 (0~2개)
            image_results = self.search_images_by_vector(
                query_embedding=query_embedding,
                threshold=threshold,
                limit=image_limit
            )
            print(f"   이미지 검색 (Google OCR): {len(image_results)}건 발견 (전체 1,337개 중)")
            
            # 3. 결합 및 정렬
            all_results = news_results + image_results
            all_results.sort(key=lambda x: x['similarity'], reverse=True)
            
            # 4. 상위 N개만 반환
            top_results = all_results[:limit]
            
            print(f"✅ Vector Search 완료: {len(top_results)}건 반환")
            
            return top_results
            
        except Exception as e:
            print(f"❌ Vector Search 오류: {e}")
            import traceback
            traceback.print_exc()
            return []
