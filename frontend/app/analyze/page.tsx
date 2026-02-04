"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Header from "../components/Header";
import { analyzeMessage } from "../lib/api";

export default function AnalyzePage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const performAnalysis = async () => {
      const message = localStorage.getItem("currentMessage") || "";
      
      if (!message) {
        router.push("/");
        return;
      }

      try {
        // 실제 백엔드 API 호출
        const apiResult = await analyzeMessage(message);
        
        // 결과 변환 (프론트엔드 형식으로)
        const result = {
          message,
          timestamp: apiResult.analyzed_at,
          riskLevel: apiResult.risk_level === "critical" || apiResult.risk_level === "high" ? "high" : "safe",
          score: apiResult.risk_score,
          phishingType: apiResult.phishing_type,
          matchedRules: apiResult.matched_rules,
          recommendations: apiResult.recommendations,
          urlCheckResults: apiResult.url_check_results,
        };
        
        localStorage.setItem("lastResult", JSON.stringify(result));
        
        // 내역에 추가
        const history = JSON.parse(localStorage.getItem("scanHistory") || "[]");
        history.unshift(result);
        localStorage.setItem("scanHistory", JSON.stringify(history));

        // 결과 페이지로 이동
        setTimeout(() => {
          if (result.riskLevel === "high") {
            router.push("/result/high-risk");
          } else {
            router.push("/result/safe");
          }
        }, 2000);
      } catch (err) {
        console.error("분석 오류:", err);
        setError("분석 중 오류가 발생했습니다. 다시 시도해주세요.");
        
        setTimeout(() => {
          router.push("/");
        }, 3000);
      }
    };

    performAnalysis();
  }, [router]);

  if (error) {
    return (
      <div className="min-h-screen flex flex-col bg-background-light dark:bg-background-dark">
        <Header title="오류 발생" showBack={false} showMenu={false} />
        
        <main className="flex-1 flex flex-col items-center justify-center px-4">
          <div className="bg-danger/10 p-6 rounded-full mb-4">
            <span className="material-symbols-outlined text-danger text-5xl">
              error
            </span>
          </div>
          <h2 className="text-danger text-2xl font-bold mb-2">분석 실패</h2>
          <p className="text-gray-600 dark:text-gray-400 text-center mb-4">
            {error}
          </p>
          <p className="text-gray-500 text-sm text-center">
            잠시 후 홈으로 돌아갑니다...
          </p>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-background-light dark:bg-background-dark">
      <Header title="검사 중" showBack={false} showMenu={false} />
      
      <main className="flex-1 flex flex-col items-center justify-center px-4">
        <div className="relative mb-8">
          <div className="animate-spin rounded-full h-24 w-24 border-4 border-primary/20 border-t-primary"></div>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="material-symbols-outlined text-primary text-4xl">
              shield_locked
            </span>
          </div>
        </div>
        
        <h2 className="text-primary dark:text-white text-2xl font-bold mb-2">
          메시지 분석 중
        </h2>
        <p className="text-gray-600 dark:text-gray-400 text-center mb-8">
          피싱 위험도를 확인하고 있습니다
        </p>

        <div className="w-full max-w-md space-y-4">
          <div className="flex items-center gap-3 p-4 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
            <div className="flex-shrink-0 w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center">
              <span className="material-symbols-outlined text-primary text-lg">
                check_circle
              </span>
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                키워드 분석 완료
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 p-4 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
            <div className="flex-shrink-0 w-8 h-8">
              <div className="animate-spin rounded-full h-8 w-8 border-2 border-primary/20 border-t-primary"></div>
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                URL 검증 중...
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 p-4 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 opacity-50">
            <div className="flex-shrink-0 w-8 h-8 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center">
              <span className="material-symbols-outlined text-gray-400 text-lg">
                schedule
              </span>
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                데이터베이스 대조 대기 중
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
