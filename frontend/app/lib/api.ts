/**
 * API 클라이언트
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8888';

export interface AnalyzeResponse {
  risk_score: number;
  risk_level: string;
  is_phishing: boolean;
  phishing_type: string | null;
  matched_rules: Array<{
    category: string;
    matched_keyword: string;
    score: number;
    description: string;
  }>;
  url_check_results: Array<{
    url: string;
    is_safe: boolean;
    threat_type: string | null;
    score: number;
  }>;
  recommendations: string[];
  analyzed_at: string;
  // 벡터 검색 결과
  similar_cases_count?: number;
  db_similarity_score?: number;
  llm_analysis?: {
    is_phishing: boolean;
    risk_score: number;
    confidence: number;
    phishing_type: string;
    reasoning: string;
  } | null;
}

export async function analyzeMessage(message: string): Promise<AnalyzeResponse> {
  const response = await fetch(`${API_URL}/api/v1/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    throw new Error('분석 요청 실패');
  }

  return response.json();
}

export interface StatsResponse {
  total_news: number;
  total_images: number;
  recent_phishing_types: Array<{ type: string; count: number }>;
  daily_stats: Array<any>;
}

export async function getStats(): Promise<StatsResponse> {
  const response = await fetch(`${API_URL}/api/v1/stats`);

  if (!response.ok) {
    throw new Error('통계 조회 실패');
  }

  return response.json();
}
