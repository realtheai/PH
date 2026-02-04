"""
임베딩 생성 모듈 (Gemini API)
"""
import os
from typing import List
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# API 키 로테이션
GEMINI_API_KEYS = [
    os.getenv('GEMINI_API_KEY'),
    os.getenv('GEMINI_API_KEY_2'),
    os.getenv('GEMINI_API_KEY_3'),
    os.getenv('GEMINI_API_KEY_4'),
    os.getenv('GEMINI_API_KEY_5'),
    os.getenv('GEMINI_API_KEY_6'),
]

current_key_index = 0

class Embedder:
    """임베딩 생성 클래스"""
    
    def __init__(self):
        """초기화"""
        global current_key_index
        self.api_keys = [key for key in GEMINI_API_KEYS if key]
        current_key_index = 0
        genai.configure(api_key=self.api_keys[current_key_index])
    
    def create_embedding(self, text: str, retry: int = 3) -> List[float]:
        """
        텍스트를 임베딩 벡터로 변환
        
        Args:
            text: 임베딩할 텍스트
            retry: 재시도 횟수
        
        Returns:
            1536차원 임베딩 벡터
        """
        global current_key_index
        
        # 텍스트 길이 제한
        text = text[:5000]
        
        for attempt in range(retry):
            try:
                # Gemini embedding 생성
                result = genai.embed_content(
                    model="models/text-embedding-004",
                    content=text,
                    task_type="retrieval_query"  # 쿼리용
                )
                
                embedding = result['embedding']
                
                # 1536차원으로 패딩 (Gemini는 768차원)
                if len(embedding) < 1536:
                    embedding = embedding + [0.0] * (1536 - len(embedding))
                elif len(embedding) > 1536:
                    embedding = embedding[:1536]
                
                return embedding
                
            except Exception as e:
                print(f"임베딩 생성 오류 (시도 {attempt + 1}/{retry}): {e}")
                
                # API 키 로테이션
                if len(self.api_keys) > 1:
                    current_key_index = (current_key_index + 1) % len(self.api_keys)
                    genai.configure(api_key=self.api_keys[current_key_index])
                
                if attempt == retry - 1:
                    raise Exception(f"임베딩 생성 실패: {str(e)}")
        
        return None
