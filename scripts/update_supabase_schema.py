#!/usr/bin/env python3
"""
Supabase 스키마 업데이트 실행
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')

print("\n" + "="*70)
print("🔧 Supabase 스키마 업데이트")
print("="*70 + "\n")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Supabase 환경 변수가 설정되지 않았습니다!")
    exit(1)

print(f"📍 Supabase URL: {SUPABASE_URL}")
print()

# SQL 파일 읽기
sql_file = 'database/update_schema.sql'
print(f"📄 SQL 파일 읽기: {sql_file}")

try:
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    print(f"✅ SQL 파일 읽기 성공 ({len(sql_content):,}자)\n")
except FileNotFoundError:
    print(f"❌ SQL 파일을 찾을 수 없습니다: {sql_file}")
    exit(1)

print("="*70)
print("⚠️  주의: 이 스크립트는 Supabase SQL Editor에서 직접 실행해야 합니다!")
print("="*70)
print()
print("다음 단계를 따라주세요:")
print()
print("1. Supabase 대시보드에 로그인하세요:")
print(f"   {SUPABASE_URL.replace('/rest/v1', '')}")
print()
print("2. 왼쪽 메뉴에서 'SQL Editor'를 클릭하세요")
print()
print("3. 'New query'를 클릭하세요")
print()
print("4. 다음 SQL을 복사해서 붙여넣고 'RUN'을 클릭하세요:")
print()
print("="*70)
print()
print(sql_content)
print()
print("="*70)
print()
print("5. 실행 완료 후 다음 명령으로 확인하세요:")
print("   python scripts/check_supabase_details.py")
print()
print("="*70 + "\n")

# SQL 파일을 클립보드에 복사하려면 (선택사항)
try:
    import pyperclip
    pyperclip.copy(sql_content)
    print("✅ SQL이 클립보드에 복사되었습니다!")
except ImportError:
    print("💡 Tip: pyperclip을 설치하면 SQL을 자동으로 클립보드에 복사할 수 있습니다.")
    print("   pip install pyperclip")
