"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Header from "../../components/Header";

interface AnalysisResult {
  message: string;
  timestamp: string;
  riskLevel: string;
  score: number;
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

          <section>
            <h2 className="text-primary dark:text-white text-xl font-bold leading-tight tracking-[-0.015em] px-4 pb-3 pt-4">
              분석 결과
            </h2>
            <div className="space-y-2 px-4">
              <div className="flex items-center gap-4 bg-danger/5 dark:bg-danger/10 px-4 min-h-[72px] py-3 justify-between rounded-xl border border-danger/10">
                <div className="flex items-center gap-4">
                  <div className="text-danger flex items-center justify-center rounded-lg bg-danger/10 shrink-0 size-12">
                    <span className="material-symbols-outlined">priority_high</span>
                  </div>
                  <div className="flex flex-col justify-center">
                    <p className="text-gray-900 dark:text-white text-base font-semibold leading-tight line-clamp-1">
                      긴급성 강조됨
                    </p>
                    <p className="text-danger text-sm font-normal leading-normal line-clamp-2">
                      '계정 정지'와 같은 긴급 문구가 감지됨
                    </p>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-4 bg-danger/5 dark:bg-danger/10 px-4 min-h-[72px] py-3 justify-between rounded-xl border border-danger/10">
                <div className="flex items-center gap-4">
                  <div className="text-danger flex items-center justify-center rounded-lg bg-danger/10 shrink-0 size-12">
                    <span className="material-symbols-outlined">person_search</span>
                  </div>
                  <div className="flex flex-col justify-center">
                    <p className="text-gray-900 dark:text-white text-base font-semibold leading-tight line-clamp-1">
                      개인정보 요구
                    </p>
                    <p className="text-danger text-sm font-normal leading-normal line-clamp-2">
                      비밀번호 또는 주민번호 수집 시도 감지
                    </p>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-4 bg-danger/5 dark:bg-danger/10 px-4 min-h-[72px] py-3 justify-between rounded-xl border border-danger/10">
                <div className="flex items-center gap-4">
                  <div className="text-danger flex items-center justify-center rounded-lg bg-danger/10 shrink-0 size-12">
                    <span className="material-symbols-outlined">link_off</span>
                  </div>
                  <div className="flex flex-col justify-center">
                    <p className="text-gray-900 dark:text-white text-base font-semibold leading-tight line-clamp-1">
                      의심스러운 링크
                    </p>
                    <p className="text-danger text-sm font-normal leading-normal line-clamp-2">
                      단축 URL 또는 도메인 불일치 감지
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <section className="mt-6 mb-8">
            <h2 className="text-gray-900 dark:text-white text-xl font-bold leading-tight tracking-[-0.015em] px-4 pb-3">
              권장 행동
            </h2>
            <div className="mx-4 p-4 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm space-y-3">
              <div className="flex items-start gap-3">
                <span className="material-symbols-outlined text-primary mt-0.5">
                  check_circle
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
                  security
                </span>
                <p className="text-gray-600 dark:text-gray-300 text-base font-medium">
                  이 시도를 은행이나 서비스 제공업체에 신고하세요.
                </p>
              </div>
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
