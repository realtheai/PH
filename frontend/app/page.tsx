"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Header from "./components/Header";
import BottomNav from "./components/BottomNav";

export default function Home() {
  const router = useRouter();
  const [message, setMessage] = useState("");

  useEffect(() => {
    // 공유된 메시지 확인 (Share Intent)
    const sharedMessage = localStorage.getItem("sharedMessage");
    if (sharedMessage) {
      setMessage(sharedMessage);
      localStorage.removeItem("sharedMessage");
      
      // 자동으로 검사 시작
      setTimeout(() => {
        localStorage.setItem("currentMessage", sharedMessage);
        router.push("/analyze");
      }, 1000);
    }
  }, [router]);

  const handleAnalyze = () => {
    if (!message.trim()) {
      alert("검사할 메시지를 입력해주세요.");
      return;
    }
    // 분석 페이지로 이동 (메시지를 localStorage에 저장)
    localStorage.setItem("currentMessage", message);
    router.push("/analyze");
  };

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      setMessage(text);
    } catch (err) {
      console.error("클립보드 읽기 실패:", err);
      alert("클립보드 접근 권한이 필요합니다.");
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Header showMenu={true} showHistory={true} />
      
      <main className="flex-1 overflow-y-auto pb-24">
        <div className="flex flex-col items-center pt-8 pb-4">
          <div className="bg-primary/10 dark:bg-primary/30 p-4 rounded-full mb-4">
            <span
              className="material-symbols-outlined text-primary dark:text-blue-400"
              style={{ fontSize: "48px" }}
            >
              shield_locked
            </span>
          </div>
          <h1 className="text-primary dark:text-white tracking-light text-[28px] font-bold leading-tight px-4 text-center">
            피싱체커
          </h1>
          <p className="text-gray-600 dark:text-gray-400 text-base font-normal leading-normal pb-3 pt-1 px-8 text-center">
            의심 메시지, 바로 확인하세요
          </p>
        </div>

        <div className="px-4 py-3">
          <div className="flex flex-col w-full">
            <p className="text-primary dark:text-gray-200 text-base font-medium leading-normal pb-2">
              메시지 내용
            </p>
            <textarea
              className="form-input flex w-full resize-none overflow-hidden rounded-xl text-gray-900 dark:text-gray-100 focus:outline-0 focus:ring-2 focus:ring-primary border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 min-h-[180px] placeholder:text-gray-400 p-4 text-base font-normal leading-normal shadow-sm"
              placeholder="의심되는 메시지를 붙여넣으세요"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
            />
          </div>
        </div>

        <div className="flex flex-col gap-3 px-4 py-4">
          <button
            onClick={handleAnalyze}
            className="flex items-center justify-center gap-2 bg-primary text-white font-bold py-4 px-6 rounded-xl shadow-lg active:scale-95 transition-transform"
          >
            <span className="material-symbols-outlined">search_check</span>
            검사하기
          </button>
          <button
            onClick={handlePaste}
            className="flex items-center justify-center gap-2 bg-primary/10 dark:bg-primary/20 text-primary dark:text-blue-300 font-bold py-3 px-6 rounded-xl active:scale-95 transition-transform border border-primary/20"
          >
            <span className="material-symbols-outlined">content_paste</span>
            붙여넣기
          </button>
        </div>

        <div className="px-4 mt-6">
          <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-100 dark:border-gray-700 shadow-sm">
            <div className="flex items-center gap-2 mb-3">
              <span className="material-symbols-outlined text-orange-500">
                lightbulb
              </span>
              <h3 className="font-bold text-gray-800 dark:text-gray-200">팁</h3>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2 leading-relaxed">
              긴급한 문구나 의심스러운 단축 링크를 주의하세요.
            </p>
            <div className="bg-background-light dark:bg-gray-900 p-3 rounded-lg border-l-4 border-primary/40 italic text-sm text-gray-500 dark:text-gray-400">
              "고객님 계정이 정지되었습니다. 본인확인 필요 -&gt; bit.ly/xxx"
            </div>
          </div>
        </div>
      </main>

      <BottomNav />
    </div>
  );
}
