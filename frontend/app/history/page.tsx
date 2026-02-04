"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Header from "../components/Header";
import BottomNav from "../components/BottomNav";

interface ScanRecord {
  message: string;
  timestamp: string;
  riskLevel: string;
  score: number;
}

export default function HistoryPage() {
  const router = useRouter();
  const [history, setHistory] = useState<ScanRecord[]>([]);

  useEffect(() => {
    const savedHistory = localStorage.getItem("scanHistory");
    if (savedHistory) {
      setHistory(JSON.parse(savedHistory));
    }
  }, []);

  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return "방금 전";
    if (diffMins < 60) return `${diffMins}분 전`;
    if (diffHours < 24) return `${diffHours}시간 전`;
    if (diffDays < 7) return `${diffDays}일 전`;
    
    return date.toLocaleDateString("ko-KR", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  const getRiskBadge = (riskLevel: string) => {
    if (riskLevel === "high") {
      return (
        <span className="px-3 py-1 bg-danger/10 text-danger text-xs font-bold rounded-full">
          위험
        </span>
      );
    }
    return (
      <span className="px-3 py-1 bg-success/10 text-success text-xs font-bold rounded-full">
        안전
      </span>
    );
  };

  const handleItemClick = (record: ScanRecord) => {
    localStorage.setItem("lastResult", JSON.stringify(record));
    if (record.riskLevel === "high") {
      router.push("/result/high-risk");
    } else {
      router.push("/result/safe");
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-background-light dark:bg-background-dark">
      <Header title="검사 내역" showBack={false} showMenu={true} />
      
      <main className="flex-1 overflow-y-auto pb-24 px-4 pt-4">
        {history.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20">
            <div className="bg-gray-100 dark:bg-gray-800 p-6 rounded-full mb-4">
              <span
                className="material-symbols-outlined text-gray-400 dark:text-gray-600"
                style={{ fontSize: "48px" }}
              >
                history
              </span>
            </div>
            <h3 className="text-gray-900 dark:text-white text-lg font-bold mb-2">
              검사 내역이 없습니다
            </h3>
            <p className="text-gray-500 dark:text-gray-400 text-sm text-center mb-6">
              메시지를 검사하면 여기에 기록됩니다
            </p>
            <button
              onClick={() => router.push("/")}
              className="flex items-center gap-2 bg-primary text-white font-bold py-3 px-6 rounded-xl active:scale-95 transition-transform"
            >
              <span className="material-symbols-outlined">search_check</span>
              첫 검사 시작하기
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            <div className="flex items-center justify-between mb-4">
              <p className="text-gray-600 dark:text-gray-400 text-sm">
                총 {history.length}건의 검사 기록
              </p>
              <button
                onClick={() => {
                  if (confirm("모든 검사 내역을 삭제하시겠습니까?")) {
                    localStorage.removeItem("scanHistory");
                    setHistory([]);
                  }
                }}
                className="text-danger text-sm font-medium"
              >
                전체 삭제
              </button>
            </div>

            {history.map((record, index) => (
              <div
                key={index}
                onClick={() => handleItemClick(record)}
                className="bg-white dark:bg-gray-800 p-4 rounded-xl border border-gray-200 dark:border-gray-700 cursor-pointer active:scale-98 transition-transform"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1 mr-3">
                    <p className="text-gray-900 dark:text-white font-medium line-clamp-2 mb-1">
                      {record.message.substring(0, 80)}
                      {record.message.length > 80 ? "..." : ""}
                    </p>
                    <p className="text-gray-500 dark:text-gray-400 text-xs">
                      {formatDate(record.timestamp)}
                    </p>
                  </div>
                  {getRiskBadge(record.riskLevel)}
                </div>
                <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-100 dark:border-gray-700">
                  <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-gray-400 text-sm">
                      analytics
                    </span>
                    <span className="text-gray-600 dark:text-gray-400 text-sm">
                      피싱 확률: {record.score}점
                    </span>
                  </div>
                  <span className="material-symbols-outlined text-gray-400 text-sm">
                    chevron_right
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      <BottomNav />
    </div>
  );
}
