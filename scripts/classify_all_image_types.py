#!/usr/bin/env python3
"""
모든 REAL_CASE 이미지의 피싱 유형 분류 (날짜 필터 없음)
"""
import requests
import json
import time
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal'
}

def classify_type_with_openai(text):
    """OpenAI로 피싱 유형 분류"""
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENAI_API_KEY}"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": """당신은 피싱 유형 분류 전문가입니다.

다음 유형으로 분류하세요:
1. 가족사칭 - 자녀, 부모, 친척 사칭
2. 공공기관사칭 - 경찰, 검찰, 금감원, 구청 등
3. 지인사칭 - 친구, 동료 사칭
4. 부고/경조사 - 부고, 결혼, 돌잔치 빙자
5. 정부지원금 - 코로나 지원금, 재난지원금
6. 금융/결제사기 - 대출, 카드, 계좌
7. 택배/배송사기 - CJ, 롯데택배 사칭
8. 투자사기 - 코인, 주식, 골드바
9. 기타 - 위 유형에 해당하지 않음

JSON만 출력: {"phishing_type": "유형"}"""
                    },
                    {
                        "role": "user",
                        "content": f"분류할 텍스트:\n{text[:1000]}"
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 50,
                "response_format": {"type": "json_object"}
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()['choices'][0]['message']['content']
            data = json.loads(result)
            phishing_type = data.get('phishing_type', '기타')
            return phishing_type
        else:
            return '기타'
    
    except Exception as e:
        print(f"   분류 오류: {e}")
        return '기타'

def get_all_untyped_images():
    """모든 REAL_CASE 이미지 중 유형 미분류 항목 (페이지네이션)"""
    items = []
    offset = 0
    limit = 100
    
    print("📥 이미지 데이터 수집 중...")
    
    try:
        while True:
            url = f"{SUPABASE_URL}/rest/v1/phishing_images"
            params = {
                'select': 'id,ocr_text,translated_text,translated_content,phishing_type',
                'classification': 'eq.REAL_CASE',
                'order': 'id.desc',
                'limit': str(limit),
                'offset': str(offset)
            }
            
            response = requests.get(url, headers=HEADERS, params=params, timeout=10)
            if response.status_code == 200:
                batch = response.json()
                if not batch:
                    break
                # 클라이언트 측에서 phishing_type이 null인 것만 필터링
                filtered = [item for item in batch if not item.get('phishing_type')]
                items.extend(filtered)
                print(f"   수집: {len(items)}개 (전체 {offset + len(batch)}개 중)...")
                
                # 더 이상 데이터가 없으면 종료
                if len(batch) < limit:
                    break
                offset += limit
            else:
                print(f"   ⚠️  조회 실패: {response.status_code}")
                break
        
        print(f"✅ 총 {len(items)}개 수집 완료\n")
        return items
    
    except Exception as e:
        print(f"❌ DB 조회 오류: {e}")
        return items

def update_phishing_type(record_id, phishing_type):
    """유형 업데이트"""
    try:
        url = f"{SUPABASE_URL}/rest/v1/phishing_images"
        params = {'id': f'eq.{record_id}'}
        data = {'phishing_type': phishing_type}
        
        response = requests.patch(url, headers=HEADERS, params=params, json=data, timeout=10)
        return response.status_code in [200, 204]
    
    except Exception:
        return False

def main():
    print(f"\n{'='*60}")
    print(f"🎯 전체 REAL_CASE 이미지 피싱 유형 분류")
    print(f"   모델: OpenAI gpt-4o-mini")
    print(f"{'='*60}\n")
    
    items = get_all_untyped_images()
    total = len(items)
    
    if total == 0:
        print("✅ 분류할 항목 없음 (모두 완료)\n")
        return
    
    print(f"📊 총 {total}개 이미지 처리 시작...")
    print(f"⏱️  예상 시간: {int(total * 0.6 / 60)}분\n")
    
    stats = {}
    success = 0
    failed = 0
    
    for idx, item in enumerate(items, 1):
        try:
            record_id = item['id']
            text = (
                item.get('translated_content') or 
                item.get('translated_text') or 
                item.get('ocr_text', '')
            )
            
            if not text or len(text.strip()) < 10:
                print(f"[{idx}/{total}] IMAGE ID:{record_id} - ⚠️  텍스트 없음 (건너뜀)")
                continue
            
            print(f"[{idx}/{total}] IMAGE ID:{record_id}")
            
            # 분류
            phishing_type = classify_type_with_openai(text)
            print(f"   ✅ 유형: {phishing_type}")
            
            # 업데이트
            if update_phishing_type(record_id, phishing_type):
                stats[phishing_type] = stats.get(phishing_type, 0) + 1
                success += 1
                print(f"   💾 DB 업데이트 완료")
            else:
                failed += 1
                print(f"   ⚠️  DB 업데이트 실패")
            
            # 진행 상황 표시
            if idx % 50 == 0:
                print(f"\n{'='*60}")
                print(f"📊 진행 상황: {idx}/{total} ({int(idx/total*100)}%)")
                print(f"   성공: {success}개 | 실패: {failed}개")
                print(f"{'='*60}\n")
            
            time.sleep(0.5)  # API rate limit 대비
        
        except Exception as e:
            failed += 1
            print(f"   ❌ 오류: {e}")
            continue
    
    # 최종 결과
    print(f"\n{'='*60}")
    print(f"✅ 전체 이미지 피싱 유형 분류 완료!")
    print(f"{'='*60}")
    print(f"   총 처리: {total}개")
    print(f"   성공: {success}개")
    print(f"   실패: {failed}개")
    print(f"\n📊 유형별 통계:")
    for phishing_type, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
        print(f"   - {phishing_type}: {count}개")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
