#!/usr/bin/env python3
"""
중복 데이터 제거 스크립트 (Gemini Embedding API 기반)

- Gemini text-embedding-004로 텍스트 임베딩
- Cosine Similarity로 유사도 계산
- 임계값 이상 → 중복 제거
- 최신 항목 유지
"""

import os
import json
import requests
import numpy as np
import time
from datetime import datetime
from typing import List, Dict, Tuple
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity

# 환경 변수 로드
load_dotenv()

class DataDeduplicator:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        # Gemini API 키 로드
        self.gemini_keys = []
        for i in range(1, 10):
            key = os.getenv(f'GEMINI_API_KEY_{i}')
            if key:
                self.gemini_keys.append(key)
        
        # OpenAI API 키 (fallback)
        self.openai_key = os.getenv('OPENAI_API_KEY')
        
        # Gemini 또는 OpenAI 중 하나는 있어야 함
        if not self.gemini_keys and not self.openai_key:
            raise ValueError("❌ GEMINI_API_KEY 또는 OPENAI_API_KEY가 .env에 없습니다.")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("❌ SUPABASE_URL 또는 SUPABASE_ANON_KEY가 .env에 없습니다.")
        
        self.headers = {
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json'
        }
        
        self.current_key_idx = 0
        self.use_openai = len(self.gemini_keys) == 0  # Gemini 키가 없으면 OpenAI 사용
        
        if self.use_openai:
            print(f"✅ OpenAI API 사용 (임베딩)\n")
        else:
            print(f"✅ Gemini API 키 {len(self.gemini_keys)}개 로드\n")
    
    def get_next_gemini_key(self) -> str:
        """다음 Gemini API 키 가져오기 (Round-robin)"""
        key = self.gemini_keys[self.current_key_idx]
        self.current_key_idx = (self.current_key_idx + 1) % len(self.gemini_keys)
        return key
    
    def get_embedding(self, text: str, max_retries: int = 3) -> np.ndarray:
        """텍스트 임베딩 생성 (Gemini 또는 OpenAI)"""
        if self.use_openai:
            return self.get_embedding_openai(text, max_retries)
        else:
            return self.get_embedding_gemini(text, max_retries)
    
    def get_embedding_openai(self, text: str, max_retries: int = 3) -> np.ndarray:
        """OpenAI API로 텍스트 임베딩 생성"""
        for attempt in range(max_retries):
            try:
                url = "https://api.openai.com/v1/embeddings"
                
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.openai_key}'
                }
                
                payload = {
                    "model": "text-embedding-3-small",
                    "input": text[:8000],  # OpenAI는 더 긴 텍스트 지원
                    "encoding_format": "float"
                }
                
                response = requests.post(url, json=payload, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    embedding = result['data'][0]['embedding']
                    return np.array(embedding)
                else:
                    if attempt < max_retries - 1:
                        time.sleep(1)
                        continue
                    return None
            
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                return None
        
        return None
    
    def get_embedding_gemini(self, text: str, max_retries: int = 3) -> np.ndarray:
        """Gemini API로 텍스트 임베딩 생성"""
        for attempt in range(max_retries):
            try:
                api_key = self.get_next_gemini_key()
                url = "https://generativelanguage.googleapis.com/v1/models/text-embedding-004:embedContent"
                
                payload = {
                    "model": "models/text-embedding-004",
                    "content": {
                        "parts": [{"text": text[:1000]}]  # 최대 1000자로 제한
                    }
                }
                
                headers = {
                    'Content-Type': 'application/json',
                    'x-goog-api-key': api_key
                }
                
                response = requests.post(url, json=payload, headers=headers, timeout=30)
                
                if response.status_code == 429:
                    if attempt < max_retries - 1:
                        time.sleep(1)
                        continue
                    else:
                        return None
                
                if response.status_code == 200:
                    result = response.json()
                    embedding = result.get('embedding', {}).get('values', [])
                    return np.array(embedding)
                else:
                    return None
            
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                else:
                    return None
        
        return None
    
    def get_embeddings_batch(self, texts: List[str], batch_size: int = 10) -> np.ndarray:
        """텍스트 배치를 임베딩으로 변환"""
        embeddings = []
        total = len(texts)
        
        print(f"🔄 임베딩 생성 중... (총 {total}개)")
        
        for i in range(0, total, batch_size):
            batch = texts[i:i + batch_size]
            
            for j, text in enumerate(batch):
                idx = i + j
                embedding = self.get_embedding(text)
                
                if embedding is not None:
                    embeddings.append(embedding)
                    if (idx + 1) % 10 == 0 or idx + 1 == total:
                        print(f"   진행: {idx + 1}/{total} ({(idx + 1) / total * 100:.1f}%)")
                else:
                    # 임베딩 실패 시 zero 벡터
                    print(f"   ⚠️  {idx + 1}번째 임베딩 실패, zero 벡터 사용")
                    embeddings.append(np.zeros(768))  # text-embedding-004는 768차원
                
                time.sleep(0.5)  # API rate limit 방지
        
        print(f"✅ 임베딩 생성 완료\n")
        return np.array(embeddings)
    
    def fetch_all_news(self, category: str = None) -> List[Dict]:
        """Supabase에서 뉴스 데이터 가져오기 (최근 2일, 페이지네이션)"""
        from datetime import timedelta
        
        print(f"📥 뉴스 데이터 가져오는 중 (최근 2일)...")
        
        # 최근 2일
        two_days_ago = (datetime.now() - timedelta(days=2)).isoformat()
        
        all_data = []
        offset = 0
        limit = 1000
        
        while True:
            if category:
                url = f"{self.supabase_url}/rest/v1/phishing_news?select=*&category=eq.{category}&crawled_at=gte.{two_days_ago}&order=created_at.desc&offset={offset}&limit={limit}"
            else:
                url = f"{self.supabase_url}/rest/v1/phishing_news?select=*&crawled_at=gte.{two_days_ago}&order=created_at.desc&offset={offset}&limit={limit}"
            
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                if len(data) == 0:
                    break
                all_data.extend(data)
                print(f"   진행: {len(all_data)}개...")
                offset += limit
            else:
                print(f"❌ 데이터 가져오기 실패: {response.status_code}")
                break
        
        print(f"✅ 총 {len(all_data)}개 뉴스 가져오기 완료\n")
        return all_data
    
    def create_text_for_embedding(self, item: Dict) -> str:
        """임베딩을 위한 텍스트 생성 (제목 + 내용)"""
        title = item.get('title', '')
        content = item.get('content', '')
        
        # 제목과 내용을 합침 (내용은 앞부분만 사용하여 성능 향상)
        text = f"{title}\n{content[:500]}"
        return text.strip()
    
    def find_duplicates(self, data: List[Dict], threshold: float = 0.85) -> List[Tuple[int, int, float]]:
        """중복 데이터 찾기 (Cosine Similarity 기반)"""
        print(f"🔍 중복 검사 중... (임계값: {threshold})")
        print(f"   - 총 {len(data)}개 항목 비교\n")
        
        # 1. 텍스트 추출
        texts = [self.create_text_for_embedding(item) for item in data]
        
        # 2. 임베딩 생성 (Gemini API 사용)
        embeddings = self.get_embeddings_batch(texts, batch_size=10)
        
        # 3. Cosine Similarity 계산
        print("🔄 유사도 계산 중...")
        similarity_matrix = cosine_similarity(embeddings)
        
        # 4. 중복 쌍 찾기
        duplicates = []
        n = len(data)
        
        for i in range(n):
            for j in range(i + 1, n):
                similarity = similarity_matrix[i][j]
                
                if similarity >= threshold:
                    # (이전 인덱스, 최신 인덱스, 유사도)
                    # created_at이 더 최근인 것을 최신으로 간주
                    created_i = data[i].get('created_at', '')
                    created_j = data[j].get('created_at', '')
                    
                    if created_i > created_j:
                        duplicates.append((j, i, similarity))  # j가 이전, i가 최신
                    else:
                        duplicates.append((i, j, similarity))  # i가 이전, j가 최신
        
        print(f"✅ 중복 검사 완료: {len(duplicates)}쌍 발견\n")
        return duplicates
    
    def remove_duplicates(self, data: List[Dict], duplicates: List[Tuple[int, int, float]], dry_run: bool = True):
        """중복 데이터 제거"""
        if len(duplicates) == 0:
            print("✅ 중복 데이터가 없습니다!")
            return
        
        print(f"\n{'='*70}")
        print(f"🗑️  중복 데이터 제거 {'(시뮬레이션)' if dry_run else '(실제 삭제)'}")
        print(f"{'='*70}\n")
        
        # 삭제할 항목 수집 (이전 항목만)
        to_delete = set()
        
        # 샘플만 출력 (처음 5개)
        sample_count = min(5, len(duplicates))
        
        for i, (old_idx, new_idx, similarity) in enumerate(duplicates):
            to_delete.add(old_idx)
            
            if i < sample_count:
                old_item = data[old_idx]
                new_item = data[new_idx]
                
                print(f"🔍 중복 {i+1}/{len(duplicates)} (유사도: {similarity:.3f})")
                print(f"   [삭제] ID: {old_item['id']} - {old_item.get('title', '')[:40]}...")
                print(f"   [유지] ID: {new_item['id']} - {new_item.get('title', '')[:40]}...")
                print()
        
        print(f"\n📊 요약:")
        print(f"   - 총 항목: {len(data)}개")
        print(f"   - 중복 쌍: {len(duplicates)}쌍")
        print(f"   - 삭제 대상: {len(to_delete)}개")
        print(f"   - 유지: {len(data) - len(to_delete)}개")
        
        if dry_run:
            print(f"\n⚠️  dry_run=True: 실제 삭제하지 않습니다.")
            return
        
        # 실제 삭제
        print(f"\n🗑️  Supabase에서 삭제 중...")
        deleted_count = 0
        
        for idx in to_delete:
            item = data[idx]
            item_id = item['id']
            
            delete_url = f"{self.supabase_url}/rest/v1/phishing_news?id=eq.{item_id}"
            response = requests.delete(delete_url, headers=self.headers)
            
            if response.status_code in [200, 204]:
                deleted_count += 1
                print(f"   ✅ ID {item_id} 삭제 완료 ({deleted_count}/{len(to_delete)})")
            else:
                print(f"   ❌ ID {item_id} 삭제 실패: {response.status_code}")
        
        print(f"\n🎉 삭제 완료: {deleted_count}개 삭제됨")
    
    def deduplicate_category(self, category: str, threshold: float = 0.85, dry_run: bool = True):
        """특정 카테고리의 중복 제거"""
        print(f"\n{'='*70}")
        print(f"🎯 {category} 카테고리 중복 제거")
        print(f"{'='*70}\n")
        
        # 1. 데이터 가져오기
        data = self.fetch_all_news(category=category)
        
        if len(data) < 2:
            print("⚠️  데이터가 2개 미만입니다. 중복 검사를 건너뜁니다.")
            return
        
        # 2. 중복 찾기
        duplicates = self.find_duplicates(data, threshold=threshold)
        
        # 3. 중복 제거
        self.remove_duplicates(data, duplicates, dry_run=dry_run)
    
    def deduplicate_all(self, threshold: float = 0.85, dry_run: bool = True):
        """전체 데이터 중복 제거"""
        print(f"\n{'='*70}")
        print(f"🎯 전체 데이터 중복 제거")
        print(f"{'='*70}\n")
        
        # 1. 데이터 가져오기
        data = self.fetch_all_news()
        
        if len(data) < 2:
            print("⚠️  데이터가 2개 미만입니다. 중복 검사를 건너뜁니다.")
            return
        
        # 2. 중복 찾기
        duplicates = self.find_duplicates(data, threshold=threshold)
        
        # 3. 중복 제거
        self.remove_duplicates(data, duplicates, dry_run=dry_run)


def main():
    """메인 실행"""
    print("\n" + "="*70)
    print("🧹 데이터 중복 제거 (Sentence Embedding)")
    print("="*70 + "\n")
    
    deduplicator = DataDeduplicator()
    
    # 사용 예시:
    
    # GitHub Actions용: 실제 삭제 모드
    print("\n📌 REAL_CASE 중복 제거 (자동화)")
    deduplicator.deduplicate_category(
        category='REAL_CASE',
        threshold=0.97,  # 유사도 97% 이상이면 중복 (매우 엄격)
        dry_run=False    # 실제 삭제 실행
    )
    
    # 옵션 2: 전체 데이터 중복 제거
    # print("\n📌 옵션 2: 전체 데이터 중복 제거")
    # deduplicator.deduplicate_all(
    #     threshold=0.85,
    #     dry_run=True
    # )
    
    # 옵션 3: NEWS만 중복 제거
    # deduplicator.deduplicate_category(
    #     category='NEWS',
    #     threshold=0.90,  # NEWS는 더 엄격하게
    #     dry_run=True
    # )


if __name__ == "__main__":
    main()
