"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Header from "../components/Header";

export default function ReportPage() {
  const router = useRouter();
  const [selectedMethod, setSelectedMethod] = useState<string | null>(null);

  const reportMethods = [
    {
      id: "police",
      title: "경찰청 사이버안전국",
      description: "전화 또는 온라인으로 신고",
      icon: "local_police",
      color: "danger",
      phone: "112",
      website: "https://ecrm.cyber.go.kr",
    },
    {
      id: "kisa",
      title: "한국인터넷진흥원 (KISA)",
      description: "스미싱 및 피싱 신고",
      icon: "security",
      color: "primary",
      phone: "118",
      website: "https://www.boho.or.kr",
    },
    {
      id: "fsc",
      title: "금융감독원",
      description: "금융 관련 피싱 신고",
      icon: "account_balance",
      color: "warning",
      phone: "1332",
      website: "https://www.fss.or.kr",
    },
  ];

  const handleCall = (phone: string) => {
    window.location.href = `tel:${phone}`;
  };

  const handleWebsite = (website: string) => {
    window.open(website, "_blank");
  };

  return (
    <div className="min-h-screen bg-background-light dark:bg-background-dark">
      <Header title="신고하기" showBack={true} showMenu={false} />
      
      <main className="flex-1 overflow-y-auto pb-8 px-4 pt-4">
        <div className="bg-primary/5 dark:bg-primary/10 p-4 rounded-xl mb-6 border border-primary/20">
          <div className="flex items-start gap-3">
            <span className="material-symbols-outlined text-primary text-2xl">
              warning
            </span>
            <div>
              <h3 className="text-primary dark:text-blue-300 font-bold mb-1">
                신속한 신고가 중요합니다
              </h3>
              <p className="text-gray-600 dark:text-gray-400 text-sm leading-relaxed">
                피싱 메시지를 신고하면 다른 사람들을 보호하는 데 도움이 됩니다.
                아래 기관에 신고해주세요.
              </p>
            </div>
          </div>
        </div>

        <h2 className="text-gray-900 dark:text-white text-lg font-bold mb-4">
          신고 기관 선택
        </h2>

        <div className="space-y-3 mb-6">
          {reportMethods.map((method) => (
            <div
              key={method.id}
              className={`bg-white dark:bg-gray-800 p-5 rounded-xl border-2 cursor-pointer transition-all ${
                selectedMethod === method.id
                  ? `border-${method.color}`
                  : "border-gray-200 dark:border-gray-700"
              }`}
              onClick={() => setSelectedMethod(method.id)}
            >
              <div className="flex items-start gap-4">
                <div
                  className={`flex-shrink-0 w-14 h-14 bg-${method.color}/10 rounded-xl flex items-center justify-center`}
                >
                  <span
                    className={`material-symbols-outlined text-${method.color} text-3xl`}
                  >
                    {method.icon}
                  </span>
                </div>
                <div className="flex-1">
                  <h3 className="text-gray-900 dark:text-white font-bold mb-1">
                    {method.title}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 text-sm mb-3">
                    {method.description}
                  </p>
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-1 text-gray-500 dark:text-gray-400 text-sm">
                      <span className="material-symbols-outlined text-sm">
                        call
                      </span>
                      <span>{method.phone}</span>
                    </div>
                  </div>
                </div>
                <div className="flex-shrink-0">
                  {selectedMethod === method.id ? (
                    <span className={`material-symbols-outlined text-${method.color}`}>
                      check_circle
                    </span>
                  ) : (
                    <span className="material-symbols-outlined text-gray-300 dark:text-gray-600">
                      radio_button_unchecked
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {selectedMethod && (
          <div className="space-y-3 animate-fade-in">
            <button
              onClick={() => {
                const method = reportMethods.find((m) => m.id === selectedMethod);
                if (method) handleCall(method.phone);
              }}
              className="w-full flex items-center justify-center gap-2 bg-danger text-white font-bold py-4 px-6 rounded-xl shadow-lg active:scale-95 transition-transform"
            >
              <span className="material-symbols-outlined">call</span>
              전화로 신고하기
            </button>
            <button
              onClick={() => {
                const method = reportMethods.find((m) => m.id === selectedMethod);
                if (method) handleWebsite(method.website);
              }}
              className="w-full flex items-center justify-center gap-2 bg-primary text-white font-bold py-4 px-6 rounded-xl active:scale-95 transition-transform"
            >
              <span className="material-symbols-outlined">language</span>
              웹사이트에서 신고하기
            </button>
            <button
              onClick={() => router.push("/")}
              className="w-full flex items-center justify-center gap-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 font-bold py-4 px-6 rounded-xl active:scale-95 transition-transform"
            >
              홈으로 돌아가기
            </button>
          </div>
        )}

        <div className="mt-8 p-4 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
          <h3 className="text-gray-900 dark:text-white font-bold mb-3 flex items-center gap-2">
            <span className="material-symbols-outlined text-primary">info</span>
            신고 시 준비사항
          </h3>
          <ul className="space-y-2 text-gray-600 dark:text-gray-400 text-sm">
            <li className="flex items-start gap-2">
              <span className="text-primary mt-0.5">•</span>
              <span>발신 번호 및 발신 시간</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-primary mt-0.5">•</span>
              <span>메시지 전체 내용 (스크린샷 권장)</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-primary mt-0.5">•</span>
              <span>의심되는 링크 주소 (클릭하지 말 것)</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-primary mt-0.5">•</span>
              <span>피해 발생 시 피해 내역</span>
            </li>
          </ul>
        </div>
      </main>
    </div>
  );
}
