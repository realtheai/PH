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

export default function SafeResultPage() {
  const router = useRouter();
  const [result, setResult] = useState<AnalysisResult | null>(null);
  
  // 홈으로 돌아가기 (analyze 페이지 건너뛰기)
  const handleBack = () => {
    // 메시지 복원 플래그 설정
    sessionStorage.setItem('restoreMessage', 'true');
    router.push('/');
  };

  useEffect(() => {
    const lastResult = localStorage.getItem("lastResult");
    if (lastResult) {
      setResult(JSON.parse(lastResult));
    } else {
      router.push("/");
    }
  }, [router]);

  const handleShare = async () => {
    if (!result) return;

    const shareText = `피싱체커 분석 결과\n\n위험도: ${result.riskLevel}\n점수: ${result.score}점\n\n✅ 이 메시지는 안전합니다.\n\n분석 시간: ${new Date(result.timestamp).toLocaleString('ko-KR')}`;

    try {
      // Web Share API 지원 확인
      if (navigator.share) {
        await navigator.share({
          title: '피싱체커 분석 결과',
          text: shareText,
        });
      } else {
        // 클립보드 복사 (Web Share API 미지원 시)
        await navigator.clipboard.writeText(shareText);
        alert('분석 결과가 클립보드에 복사되었습니다!');
      }
    } catch (error) {
      console.error('공유 실패:', error);
    }
  };

  if (!result) return null;

  return (
    <div className="min-h-screen bg-background-light dark:bg-background-dark">
      <div className="relative flex min-h-screen w-full flex-col max-w-[480px] mx-auto bg-background-light dark:bg-background-dark">
        <Header
          title="결과"
          showBack={true}
          showMenu={false}
          onBack={handleBack}
          rightAction={
            <button 
              onClick={handleShare}
              className="flex cursor-pointer items-center justify-center rounded-lg h-12 bg-transparent text-primary dark:text-gray-100 p-0"
            >
              <span className="material-symbols-outlined">share</span>
            </button>
          }
        />
        
        <main className="flex-1 overflow-y-auto pb-32">
          <div className="p-4">
            <div className="flex flex-col items-stretch justify-start rounded-xl shadow-sm bg-white dark:bg-gray-900 border border-success/20 overflow-hidden">
              <div className="w-full bg-success/10 flex items-center justify-center py-8">
                <div className="flex flex-col items-center">
                  <span className="material-symbols-outlined text-success text-7xl filled-icon">
                    verified_user
                  </span>
                  <p className="text-success text-2xl font-extrabold mt-2 tracking-wider">
                    안전함
                  </p>
                </div>
              </div>
              <div className="flex w-full flex-col items-stretch justify-center gap-3 p-5">
                <div className="flex flex-col gap-2">
                  <div className="flex gap-6 justify-between items-center">
                    <p className="text-gray-900 dark:text-white text-base font-bold leading-normal">
                      피싱 확률
                    </p>
                    <p className="text-success text-lg font-bold leading-normal">
                      {result.score}/100
                    </p>
                  </div>
                  <div className="h-3 w-full rounded-full bg-gray-200 dark:bg-gray-700 overflow-hidden">
                    <div
                      className="h-full rounded-full bg-success transition-all"
                      style={{ width: `${result.score}%` }}
                    ></div>
                  </div>
                  <p className="text-gray-600 dark:text-gray-400 text-sm font-medium mt-1">
                    피싱 위협이 감지되지 않았습니다. 안전한 메시지로 판단됩니다.
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
              <div className="flex items-center gap-4 bg-success/5 dark:bg-success/10 px-4 min-h-[72px] py-3 justify-between rounded-xl border border-success/10">
                <div className="flex items-center gap-4">
                  <div className="text-success flex items-center justify-center rounded-lg bg-success/10 shrink-0 size-12">
                    <span className="material-symbols-outlined">check_circle</span>
                  </div>
                  <div className="flex flex-col justify-center">
                    <p className="text-gray-900 dark:text-white text-base font-semibold leading-tight line-clamp-1">
                      정상 메시지
                    </p>
                    <p className="text-success text-sm font-normal leading-normal line-clamp-2">
                      의심스러운 키워드가 발견되지 않았습니다
                    </p>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-4 bg-success/5 dark:bg-success/10 px-4 min-h-[72px] py-3 justify-between rounded-xl border border-success/10">
                <div className="flex items-center gap-4">
                  <div className="text-success flex items-center justify-center rounded-lg bg-success/10 shrink-0 size-12">
                    <span className="material-symbols-outlined">link</span>
                  </div>
                  <div className="flex flex-col justify-center">
                    <p className="text-gray-900 dark:text-white text-base font-semibold leading-tight line-clamp-1">
                      URL 안전
                    </p>
                    <p className="text-success text-sm font-normal leading-normal line-clamp-2">
                      안전한 도메인으로 확인되었습니다
                    </p>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-4 bg-success/5 dark:bg-success/10 px-4 min-h-[72px] py-3 justify-between rounded-xl border border-success/10">
                <div className="flex items-center gap-4">
                  <div className="text-success flex items-center justify-center rounded-lg bg-success/10 shrink-0 size-12">
                    <span className="material-symbols-outlined">shield</span>
                  </div>
                  <div className="flex flex-col justify-center">
                    <p className="text-gray-900 dark:text-white text-base font-semibold leading-tight line-clamp-1">
                      개인정보 요구 없음
                    </p>
                    <p className="text-success text-sm font-normal leading-normal line-clamp-2">
                      민감한 정보 요청이 없습니다
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <section className="mt-6 mb-8">
            <h2 className="text-gray-900 dark:text-white text-xl font-bold leading-tight tracking-[-0.015em] px-4 pb-3">
              주의사항
            </h2>
            <div className="mx-4 p-4 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm space-y-3">
              <div className="flex items-start gap-3">
                <span className="material-symbols-outlined text-warning mt-0.5">
                  info
                </span>
                <p className="text-gray-600 dark:text-gray-300 text-base font-medium">
                  안전하다고 판단되었지만, 의심스러운 점이 있다면 발신자에게 직접 확인하세요.
                </p>
              </div>
              <div className="flex items-start gap-3">
                <span className="material-symbols-outlined text-warning mt-0.5">
                  visibility
                </span>
                <p className="text-gray-600 dark:text-gray-300 text-base font-medium">
                  개인정보를 요구하거나 긴급하게 행동을 요구하는 경우 추가 확인이 필요합니다.
                </p>
              </div>
            </div>
          </section>
        </main>

        <footer className="fixed bottom-0 left-0 right-0 max-w-[480px] mx-auto bg-background-light/95 dark:bg-background-dark/95 backdrop-blur-md p-4 border-t border-gray-200 dark:border-gray-800">
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
