"""
모든 크롤러를 통합 실행하는 메인 스크립트
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(str(Path(__file__).parent.parent))

from scripts.crawl_kisa_spam import KISASpamCrawler
from scripts.crawl_kisa_boho import KISABohoCrawler


def merge_data(data_list):
    """여러 데이터 소스를 하나로 병합"""
    merged = []
    for data in data_list:
        merged.extend(data)
    return merged


def main():
    print("="*60)
    print("🚀 피싱 데이터 수집 시작")
    print("="*60)
    print()
    
    all_data = []
    
    # 1. KISA 불법스팸대응센터 크롤링
    print("1️⃣ KISA 불법스팸대응센터")
    print("-" * 60)
    try:
        spam_crawler = KISASpamCrawler()
        spam_data = spam_crawler.run()
        all_data.append(spam_data)
    except Exception as e:
        print(f"✗ KISA 스팸센터 크롤링 실패: {e}")
    
    print("\n")
    
    # 2. KISA 보호나라 크롤링
    print("2️⃣ KISA 보호나라")
    print("-" * 60)
    try:
        boho_crawler = KISABohoCrawler()
        boho_data = boho_crawler.run()
        all_data.append(boho_data)
    except Exception as e:
        print(f"✗ KISA 보호나라 크롤링 실패: {e}")
    
    print("\n")
    
    # 3. 전체 데이터 병합 및 저장
    print("="*60)
    print("📊 최종 결과")
    print("="*60)
    
    merged_data = merge_data(all_data)
    
    if merged_data:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"data/raw/phishing_data_all_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 통합 데이터 저장: {output_file}")
        print(f"   총 수집 건수: {len(merged_data)}건")
        
        # 카테고리별 통계
        categories = {}
        for item in merged_data:
            cat = item.get('category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        print(f"\n📈 카테고리별 통계:")
        for cat, count in categories.items():
            print(f"   • {cat}: {count}건")
        
        # 키워드 통계
        all_keywords = []
        for item in merged_data:
            all_keywords.extend(item.get('keywords', []))
        
        if all_keywords:
            from collections import Counter
            keyword_counts = Counter(all_keywords)
            print(f"\n🔑 주요 키워드 (Top 10):")
            for keyword, count in keyword_counts.most_common(10):
                print(f"   • {keyword}: {count}회")
    else:
        print("⚠️  수집된 데이터가 없습니다.")
    
    print("\n✅ 크롤링 완료!")


if __name__ == "__main__":
    main()
