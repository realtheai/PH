"""
임베딩 생성 모듈 (OpenAI API)
"""
import os
from typing import List
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

class Embedder:
    """임베딩 생성 클래스 (OpenAI)"""
    
    def __init__(self):
        """초기화"""
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        print("✅ Embedder 초기화: OpenAI text-embedding-3-small")
    
    def create_embedding(self, text: str, retry: int = 3) -> List[float]:
        """
        텍스트를 임베딩 벡터로 변환 (OpenAI)
        
        Args:
            text: 임베딩할 텍스트
            retry: 재시도 횟수
        
        Returns:
            1536차원 임베딩 벡터
        """
        # 텍스트 길이 제한
        text = text[:8000]
        
        for attempt in range(retry):
            try:
                # OpenAI embedding 생성
                response = self.client.embeddings.create(
                    model="text-embedding-3-small",
                    input=text,
                    encoding_format="float"
                )
                
                embedding = response.data[0].embedding
                
                # 1536차원 확인
                if len(embedding) != 1536:
                    raise Exception(f"임베딩 차원 오류: {len(embedding)} != 1536")
                
                return embedding
                
            except Exception as e:
                print(f"임베딩 생성 오류 (시도 {attempt + 1}/{retry}): {e}")
                
                if attempt == retry - 1:
                    raise Exception(f"임베딩 생성 실패: {str(e)}")
        
        return None
