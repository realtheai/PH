"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Header from "../../components/Header";

interface AnalysisResult {
  message: string;
  timestamp: string;
  riskLevel: string;
  score: number;
  phishingType?: string | null;
  matchedRules?: Array<{
    category: string;
    matched_keyword: string;
    score: number;
    description: string;
  }>;
  recommendations?: string[];
  urlCheckResults?: Array<any>;
  // 벡터 검색 결과
  similarCasesCount?: number;
  dbSimilarityScore?: number;
  llmAnalysis?: {
    is_phishing: boolean;
    risk_score: number;
    confidence: number;
    phishing_type: string;
    reasoning: string;
  } | null;
}

export default function HighRiskResultPage() {
  const router = useRouter();
  const [result, setResult] = useState<AnalysisResult | null>(null);

  useEffect(() => {
    const lastResult = localStorage.getItem("lastResult");
    if (lastResult) {
      setResult(JSON.parse(lastResult));
    } else {
      router.push("/");
    }
  }, [router]);

  if (!result) return null;

  return (
    <div className="min-h-screen bg-background-light dark:bg-background-dark">
      <div className="relative flex min-h-screen w-full flex-col max-w-[480px] mx-auto bg-background-light dark:bg-background-dark">
        <Header
          title="결과"
          showBack={true}
          showMenu={false}
          rightAction={
            <button className="flex cursor-pointer items-center justify-center rounded-lg h-12 bg-transparent text-primary dark:text-gray-100 p-0">
              <span className="material-symbols-outlined">share</span>
            </button>
          }
        />
        
        <main className="flex-1 overflow-y-auto pb-40">
          <div className="p-4">
            <div className="flex flex-col items-stretch justify-start rounded-xl shadow-sm bg-white dark:bg-gray-900 border border-danger/20 overflow-hidden">
              <div className="w-full bg-danger/10 flex items-center justify-center py-8">
                <div className="flex flex-col items-center">
                  <span className="material-symbols-outlined text-danger text-7xl filled-icon">
                    warning
                  </span>
                  <p className="text-danger text-2xl font-extrabold mt-2 tracking-wider">
                    위험도: 높음
                  </p>
                </div>
              </div>
              <div className="flex w-full flex-col items-stretch justify-center gap-3 p-5">
                <div className="flex flex-col gap-2">
                  <div className="flex gap-6 justify-between items-center">
                    <p className="text-gray-900 dark:text-white text-base font-bold leading-normal">
                      피싱 확률
                    </p>
                    <p className="text-danger text-lg font-bold leading-normal">
                      {result.score}/100
                    </p>
                  </div>
                  <div className="h-3 w-full rounded-full bg-gray-200 dark:bg-gray-700 overflow-hidden">
                    <div
                      className="h-full rounded-full bg-danger transition-all"
                      style={{ width: `${result.score}%` }}
                    ></div>
                  </div>
                  <p className="text-gray-600 dark:text-gray-400 text-sm font-medium mt-1">
                    즉각적인 위협이 감지되었습니다. 데이터 도용 및 사기 위험이 높습니다.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* 피싱 유형 */}
          {result.phishingType && (
            <section className="mt-4">
              <div className="mx-4 p-4 bg-danger/5 dark:bg-danger/10 rounded-xl border border-danger/20">
                <div className="flex items-center gap-3">
                  <span className="material-symbols-outlined text-danger text-3xl">
                    category
                  </span>
                  <div>
                    <p className="text-gray-600 dark:text-gray-400 text-sm font-medium">
                      피싱 유형
                    </p>
                    <p className="text-danger text-lg font-bold">
                      {result.phishingType}
                    </p>
                  </div>
                </div>
              </div>
            </section>
          )}

          {/* 벡터 검색 결과 */}
          {result.similarCasesCount && result.similarCasesCount > 0 && (
            <section className="mt-4">
              <h2 className="text-primary dark:text-white text-xl font-bold leading-tight tracking-[-0.015em] px-4 pb-3 pt-4">
                유사 사례 발견
              </h2>
              <div className="mx-4 p-4 bg-primary/5 dark:bg-primary/10 rounded-xl border border-primary/20">
                <div className="flex items-center gap-3 mb-3">
                  <span className="material-symbols-outlined text-primary text-3xl">
                    database
                  </span>
                  <div>
                    <p className="text-primary text-2xl font-bold">
                      {result.similarCasesCount}건
                    </p>
                    <p className="text-gray-600 dark:text-gray-400 text-sm font-medium">
                      유사한 피싱 사례가 DB에서 발견되었습니다
                    </p>
                  </div>
                </div>
                <div className="mt-3 pt-3 border-t border-primary/20">
                  <div className="flex justify-between items-center">
                    <p className="text-gray-700 dark:text-gray-300 text-sm font-medium">
                      DB 유사도 점수
                    </p>
                    <p className="text-primary text-lg font-bold">
                      +{result.dbSimilarityScore}점
                    </p>
                  </div>
                  <p className="text-gray-500 dark:text-gray-400 text-xs mt-1">
                    과거 신고된 피싱 사례와 {((result.dbSimilarityScore || 0) * 2)}% 유사합니다
                  </p>
                </div>
              </div>
            </section>
          )}

          {/* AI 분석 결과 */}
          {result.llmAnalysis && (
            <section className="mt-4">
              <h2 className="text-primary dark:text-white text-xl font-bold leading-tight tracking-[-0.015em] px-4 pb-3">
                🤖 AI 분석
              </h2>
              <div className="mx-4 p-4 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800">
                <div className="flex items-start gap-3 mb-3">
                  <span className="material-symbols-outlined text-primary text-2xl mt-0.5">
                    psychology
                  </span>
                  <div>
                    <p className="text-gray-900 dark:text-white text-base font-semibold mb-1">
                      확신도: {(result.llmAnalysis.confidence * 100).toFixed(0)}%
                    </p>
                    <p className="text-gray-600 dark:text-gray-400 text-sm leading-relaxed">
                      {result.llmAnalysis.reasoning}
                    </p>
                  </div>
                </div>
              </div>
            </section>
          )}

          {/* 탐지된 위험 요소 */}
          <section>
            <h2 className="text-primary dark:text-white text-xl font-bold leading-tight tracking-[-0.015em] px-4 pb-3 pt-4">
              탐지된 위험 요소
            </h2>
            <div className="space-y-2 px-4">
              {result.matchedRules && result.matchedRules.length > 0 ? (
                result.matchedRules.slice(0, 5).map((rule, index) => (
                  <div key={index} className="flex items-center gap-4 bg-danger/5 dark:bg-danger/10 px-4 min-h-[72px] py-3 justify-between rounded-xl border border-danger/10">
                    <div className="flex items-center gap-4">
                      <div className="text-danger flex items-center justify-center rounded-lg bg-danger/10 shrink-0 size-12">
                        <span className="material-symbols-outlined">
                          {rule.category === '긴급성' ? 'priority_high' : 
                           rule.category === '개인정보' ? 'person_search' :
                           rule.category === 'URL' ? 'link' : 'warning'}
                        </span>
                      </div>
                      <div className="flex flex-col justify-center flex-1">
                        <p className="text-gray-900 dark:text-white text-base font-semibold leading-tight line-clamp-1">
                          {rule.category}
                        </p>
                        <p className="text-danger text-sm font-normal leading-normal line-clamp-2">
                          {rule.description}
                        </p>
                      </div>
                      <div className="text-danger text-sm font-bold">
                        +{rule.score}점
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="flex items-center gap-4 bg-danger/5 dark:bg-danger/10 px-4 min-h-[72px] py-3 justify-between rounded-xl border border-danger/10">
                  <div className="flex items-center gap-4">
                    <div className="text-danger flex items-center justify-center rounded-lg bg-danger/10 shrink-0 size-12">
                      <span className="material-symbols-outlined">warning</span>
                    </div>
                    <div className="flex flex-col justify-center">
                      <p className="text-gray-900 dark:text-white text-base font-semibold leading-tight">
                        피싱 패턴 감지됨
                      </p>
                      <p className="text-danger text-sm font-normal leading-normal">
                        AI가 피싱 가능성이 높다고 판단했습니다
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </section>

          <section className="mt-6 mb-8">
            <h2 className="text-gray-900 dark:text-white text-xl font-bold leading-tight tracking-[-0.015em] px-4 pb-3">
              권장 행동
            </h2>
            <div className="mx-4 p-4 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm space-y-3">
              {result.recommendations && result.recommendations.length > 0 ? (
                result.recommendations.slice(0, 5).map((recommendation, index) => (
                  <div key={index} className="flex items-start gap-3">
                    <span className="material-symbols-outlined text-primary mt-0.5">
                      {recommendation.includes('🤖') || recommendation.includes('AI') ? 'psychology' :
                       recommendation.includes('📊') || recommendation.includes('DB') ? 'database' :
                       recommendation.includes('링크') || recommendation.includes('클릭') ? 'link_off' :
                       recommendation.includes('차단') || recommendation.includes('삭제') ? 'block' :
                       recommendation.includes('신고') ? 'local_police' :
                       'check_circle'}
                    </span>
                    <p className="text-gray-600 dark:text-gray-300 text-base font-medium">
                      {recommendation}
                    </p>
                  </div>
                ))
              ) : (
                <>
                  <div className="flex items-start gap-3">
                    <span className="material-symbols-outlined text-primary mt-0.5">
                      link_off
                    </span>
                    <p className="text-gray-600 dark:text-gray-300 text-base font-medium">
                      링크를 클릭하거나 첨부파일을 다운로드하지 마세요.
                    </p>
                  </div>
                  <div className="flex items-start gap-3">
                    <span className="material-symbols-outlined text-primary mt-0.5">
                      block
                    </span>
                    <p className="text-gray-600 dark:text-gray-300 text-base font-medium">
                      발신번호를 차단하고 메시지를 즉시 삭제하세요.
                    </p>
                  </div>
                  <div className="flex items-start gap-3">
                    <span className="material-symbols-outlined text-primary mt-0.5">
                      local_police
                    </span>
                    <p className="text-gray-600 dark:text-gray-300 text-base font-medium">
                      이 시도를 은행이나 서비스 제공업체에 신고하세요.
                    </p>
                  </div>
                </>
              )}
            </div>
          </section>
        </main>

        <footer className="fixed bottom-0 left-0 right-0 max-w-[480px] mx-auto bg-background-light/95 dark:bg-background-dark/95 backdrop-blur-md p-4 flex flex-col gap-3 border-t border-gray-200 dark:border-gray-800">
          <button
            onClick={() => router.push("/report")}
            className="w-full flex items-center justify-center rounded-xl h-14 bg-danger text-white text-base font-bold transition-transform active:scale-95 shadow-lg shadow-danger/20"
          >
            <span className="material-symbols-outlined mr-2">local_police</span>
            경찰청에 신고하기
          </button>
          <button
            onClick={() => router.push("/")}
            className="w-full flex items-center justify-center rounded-xl h-14 bg-primary text-white text-base font-bold transition-transform active:scale-95"
          >
            <span className="material-symbols-outlined mr-2">search</span>
            다른 메시지 검사
          </button>
        </footer>
      </div>
    </div>
  );
}
