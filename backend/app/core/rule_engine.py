"""
룰 기반 피싱 검사 엔진
"""
import json
import os
from typing import List, Dict, Tuple

class RuleEngine:
    def __init__(self):
        # 룰 파일 로드 (Docker 환경 고려)
        # /app/app/core/ 에서 ../../ = /app/ 로 가서 data/rules/ 접근
        rules_path = os.path.join(os.path.dirname(__file__), '../../data/rules/rules.json')
        entities_path = os.path.join(os.path.dirname(__file__), '../../data/rules/entities_ko.json')
        
        with open(rules_path, 'r', encoding='utf-8') as f:
            rules_data = json.load(f)
            self.keyword_rules = rules_data['rules']
            self.url_patterns = rules_data['url_patterns']
        
        with open(entities_path, 'r', encoding='utf-8') as f:
            self.entities = json.load(f)
    
    def check_message(self, message: str) -> Tuple[int, List[Dict]]:
        """
        메시지 검사
        
        Returns:
            (총 점수, 매칭된 룰 리스트)
        """
        total_score = 0
        matched_rules = []
        
        message_lower = message.lower()
        
        # 키워드 룰 검사
        for rule in self.keyword_rules:
            keyword = rule['keyword']
            if keyword in message or keyword.lower() in message_lower:
                total_score += rule['score']
                matched_rules.append({
                    'category': rule['category'],
                    'matched_keyword': keyword,
                    'score': rule['score'],
                    'description': rule['description']
                })
        
        return total_score, matched_rules
    
    def check_urls(self, urls: List[str]) -> Tuple[int, List[Dict]]:
        """URL 패턴 검사 (단축 URL 등)"""
        total_score = 0
        matched_patterns = []
        
        for url in urls:
            for pattern in self.url_patterns:
                if pattern['pattern'] in url:
                    total_score += pattern['score']
                    matched_patterns.append({
                        'category': 'URL',
                        'matched_keyword': pattern['pattern'],
                        'score': pattern['score'],
                        'description': pattern['description']
                    })
        
        return total_score, matched_patterns
    
    def detect_phishing_type(self, message: str, matched_rules: List[Dict]) -> str:
        """피싱 유형 감지"""
        categories = [rule['category'] for rule in matched_rules]
        
        if '기관사칭' in categories:
            # 어떤 기관인지 확인
            for entity_type, entities in self.entities.items():
                for entity in entities:
                    if entity in message:
                        if entity_type == 'government':
                            return '정부기관사칭'
                        elif entity_type == 'banks':
                            return '금융기관사칭'
                        elif entity_type == 'delivery':
                            return '택배사칭'
            return '기관사칭'
        
        elif '금전요구' in categories:
            if '상품권' in message:
                return '상품권사기'
            return '금전요구'
        
        elif '협박' in categories:
            return '협박형피싱'
        
        return '의심'
