"""
LLM 분석 직접 테스트
"""
import sys
sys.path.append('backend')

from app.core.llm_analyzer import LLMAnalyzer

analyzer = LLMAnalyzer()

message = "긴급! 국세청입니다. 세금 환급이 있습니다. 링크를 클릭하세요"

print("=" * 60)
print("LLM 분석 테스트")
print("=" * 60)
print(f"\n메시지: {message}")

result = analyzer.analyze_message(message)

print(f"\n결과:")
import json
print(json.dumps(result, ensure_ascii=False, indent=2))
