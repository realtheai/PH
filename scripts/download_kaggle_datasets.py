"""
Kaggle 피싱 데이터셋 검색 및 다운로드 스크립트
환경 변수에서 Kaggle 인증 정보를 로드하여 사용
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from kaggle.api.kaggle_api_extended import KaggleApi

# .env 파일 로드
load_dotenv()

# Kaggle 인증 설정
os.environ['KAGGLE_USERNAME'] = os.getenv('KAGGLE_USERNAME')
os.environ['KAGGLE_KEY'] = os.getenv('KAGGLE_KEY')


class KaggleDatasetDownloader:
    def __init__(self):
        self.api = KaggleApi()
        self.api.authenticate()
        print("✅ Kaggle API 인증 완료")
        print(f"   사용자: {os.getenv('KAGGLE_USERNAME')}\n")
    
    def search_datasets(self, keywords, max_results=10):
        """데이터셋 검색"""
        all_results = []
        
        for keyword in keywords:
            print(f"\n{'='*70}")
            print(f"🔍 검색 키워드: '{keyword}'")
            print('='*70)
            
            try:
                datasets = self.api.dataset_list(search=keyword)
                
                for i, dataset in enumerate(datasets[:max_results], 1):
                    result = {
                        'rank': i,
                        'keyword': keyword,
                        'ref': dataset.ref,
                        'title': dataset.title,
                        'downloads': dataset.downloadCount if hasattr(dataset, 'downloadCount') else 0,
                        'votes': dataset.voteCount if hasattr(dataset, 'voteCount') else 0,
                        'url': f"https://www.kaggle.com/datasets/{dataset.ref}"
                    }
                    
                    all_results.append(result)
                    
                    print(f"\n{i}. {dataset.title}")
                    print(f"   📦 Ref: {dataset.ref}")
                    print(f"   ⬇️  다운로드: {result['downloads']}")
                    print(f"   ⭐ 투표: {result['votes']}")
                
                print(f"\n총 {len(datasets)} 개의 데이터셋 발견 (상위 {max_results}개 표시)")
                
            except Exception as e:
                print(f"❌ 검색 실패: {keyword} - {e}")
                continue
        
        return all_results
    
    def download_dataset(self, dataset_ref, output_dir='data/raw/kaggle'):
        """데이터셋 다운로드"""
        print(f"\n{'='*70}")
        print(f"⬇️  다운로드 시작: {dataset_ref}")
        print('='*70)
        
        # 출력 디렉토리 생성
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            print(f"   다운로드 위치: {output_dir}/{dataset_ref.replace('/', '_')}/")
            
            # 다운로드
            self.api.dataset_download_files(
                dataset_ref,
                path=f"{output_dir}/{dataset_ref.replace('/', '_')}/",
                unzip=True,
                quiet=False
            )
            
            print(f"\n✅ 다운로드 완료: {dataset_ref}")
            return True
            
        except Exception as e:
            print(f"\n❌ 다운로드 실패: {dataset_ref}")
            print(f"   에러: {e}")
            return False
    
    def save_search_results(self, results, filename='data/raw/kaggle_search_results.json'):
        """검색 결과 저장"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        data = {
            'search_date': datetime.now().isoformat(),
            'total_results': len(results),
            'datasets': results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 검색 결과 저장: {filename}")


def main():
    print("="*70)
    print("🚀 Kaggle 피싱 데이터셋 다운로더")
    print("="*70)
    
    downloader = KaggleDatasetDownloader()
    
    # 1. 검색 키워드
    keywords = [
        'phishing',
        'smishing',
        'spam sms',
        'fraud text',
        'phishing email',
        'malicious text'
    ]
    
    # 2. 데이터셋 검색
    print("\n" + "="*70)
    print("📊 단계 1: 데이터셋 검색")
    print("="*70)
    
    search_results = downloader.search_datasets(keywords, max_results=5)
    downloader.save_search_results(search_results)
    
    # 3. 추천 데이터셋 다운로드 (작은 것만)
    print("\n" + "="*70)
    print("📥 단계 2: 추천 데이터셋 다운로드")
    print("="*70)
    
    recommended_datasets = [
        'shashwatwork/phishing-dataset-for-machine-learning',  # ~234KB
        'uciml/sms-spam-collection-dataset',  # SMS 스팸
        'galactus007/sms-smishing-collection-data-set',  # 스미싱
    ]
    
    success_count = 0
    for dataset_ref in recommended_datasets:
        if downloader.download_dataset(dataset_ref):
            success_count += 1
    
    # 4. 결과 요약
    print("\n" + "="*70)
    print("📊 다운로드 결과 요약")
    print("="*70)
    print(f"   총 검색 키워드: {len(keywords)}개")
    print(f"   발견된 데이터셋: {len(search_results)}개")
    print(f"   다운로드 시도: {len(recommended_datasets)}개")
    print(f"   다운로드 성공: {success_count}개")
    print("\n✅ 완료!")


if __name__ == "__main__":
    main()
