"""
네이버 데이터 품질 개선 스크립트
- 짧은 본문(<200자) 필터링
- 유효한 데이터만 추출
"""
import json
from datetime import datetime

def clean_naver_data(input_file, output_file):
    print("="*60)
    print("🧹 네이버 데이터 정제 시작")
    print("="*60)
    
    # 데이터 로드
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"\n📊 원본 데이터: {len(data)}건")
    
    # 필터링 기준
    # 1. 본문 길이 200자 이상
    # 2. "기사 섹션 분류 안내" 같은 메타 정보 제외
    invalid_patterns = [
        "기사 섹션 분류 안내",
        "프리미엄콘텐츠는 네이버가",
        "유료\n\n프리미엄콘텐츠",
        "기사의 섹션 정보는"
    ]
    
    valid_data = []
    filtered_short = 0
    filtered_invalid = 0
    
    for item in data:
        content = item['content']
        content_length = item['content_length']
        
        # 짧은 본문 필터링
        if content_length < 200:
            filtered_short += 1
            continue
        
        # 무효한 패턴 필터링
        if any(pattern in content for pattern in invalid_patterns):
            filtered_invalid += 1
            continue
        
        valid_data.append(item)
    
    # 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(valid_data, f, ensure_ascii=False, indent=2)
    
    # 통계
    print(f"\n🔍 필터링 결과:")
    print(f"   짧은 본문(<200자): {filtered_short}건 제거")
    print(f"   무효한 패턴:        {filtered_invalid}건 제거")
    print(f"   ━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"   총 제거:           {filtered_short + filtered_invalid}건")
    print(f"   유효 데이터:       {len(valid_data)}건 ✅")
    print(f"   유효율:            {len(valid_data)/len(data)*100:.1f}%")
    
    print(f"\n💾 저장 완료: {output_file}")
    
    # 길이별 통계
    very_short = [d for d in valid_data if d['content_length'] < 500]
    medium = [d for d in valid_data if 500 <= d['content_length'] < 1500]
    long_content = [d for d in valid_data if d['content_length'] >= 1500]
    
    print(f"\n📊 정제된 데이터 품질:")
    print(f"   짧음 (200-500자):   {len(very_short):4d}건 ({len(very_short)/len(valid_data)*100:.1f}%)")
    print(f"   중간 (500-1500자):  {len(medium):4d}건 ({len(medium)/len(valid_data)*100:.1f}%)")
    print(f"   길음 (1500자+):      {len(long_content):4d}건 ({len(long_content)/len(valid_data)*100:.1f}%) ✅")
    
    return valid_data

if __name__ == "__main__":
    input_file = "data/raw/naver_api_2025-02-01_to_2026-01-31.json"
    output_file = "data/processed/naver_api_cleaned.json"
    
    import os
    os.makedirs("data/processed", exist_ok=True)
    
    clean_naver_data(input_file, output_file)
    
    print("\n" + "="*60)
    print("✅ 정제 완료!")
    print("="*60)
