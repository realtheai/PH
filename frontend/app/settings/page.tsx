"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Header from "../components/Header";
import BottomNav from "../components/BottomNav";

export default function SettingsPage() {
  const router = useRouter();
  const [darkMode, setDarkMode] = useState(false);
  const [notifications, setNotifications] = useState(true);
  const [autoScan, setAutoScan] = useState(false);
  const [showPrivacyModal, setShowPrivacyModal] = useState(false);

  useEffect(() => {
    // Load settings from localStorage
    const savedDarkMode = localStorage.getItem("darkMode") === "true";
    const savedNotifications = localStorage.getItem("notifications") !== "false";
    const savedAutoScan = localStorage.getItem("autoScan") === "true";

    setDarkMode(savedDarkMode);
    setNotifications(savedNotifications);
    setAutoScan(savedAutoScan);

    // Apply dark mode
    if (savedDarkMode) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, []);

  const handleDarkModeToggle = () => {
    const newValue = !darkMode;
    setDarkMode(newValue);
    localStorage.setItem("darkMode", String(newValue));
    
    if (newValue) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  };

  const handleNotificationsToggle = () => {
    const newValue = !notifications;
    setNotifications(newValue);
    localStorage.setItem("notifications", String(newValue));
  };

  const handleAutoScanToggle = () => {
    const newValue = !autoScan;
    setAutoScan(newValue);
    localStorage.setItem("autoScan", String(newValue));
  };

  const handleClearHistory = () => {
    console.log("🗑️ handleClearHistory called"); // 디버그 로그
    if (confirm("모든 검사 내역을 삭제하시겠습니까?")) {
      localStorage.removeItem("scanHistory");
      alert("검사 내역이 삭제되었습니다.");
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-background-light dark:bg-background-dark">
      <Header title="설정" showBack={false} showMenu={true} />
      
      <main className="flex-1 overflow-y-auto pb-24 px-4 pt-4">
        <section className="mb-6">
          <h3 className="text-gray-900 dark:text-white text-sm font-bold mb-3 px-2">
            일반 설정
          </h3>
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 divide-y divide-gray-200 dark:divide-gray-700">
            <div className="flex items-center justify-between p-4">
              <div className="flex items-center gap-3">
                <span className="material-symbols-outlined text-gray-600 dark:text-gray-400">
                  dark_mode
                </span>
                <div>
                  <p className="text-gray-900 dark:text-white font-medium">
                    다크 모드
                  </p>
                  <p className="text-gray-500 dark:text-gray-400 text-xs">
                    화면 테마 변경
                  </p>
                </div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={darkMode}
                  onChange={handleDarkModeToggle}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-300 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-primary rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
              </label>
            </div>

            <div className="flex items-center justify-between p-4">
              <div className="flex items-center gap-3">
                <span className="material-symbols-outlined text-gray-600 dark:text-gray-400">
                  notifications
                </span>
                <div>
                  <p className="text-gray-900 dark:text-white font-medium">
                    알림 (MVP 이후)
                  </p>
                  <p className="text-gray-500 dark:text-gray-400 text-xs">
                    위험 감지 시 알림 받기
                  </p>
                </div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={notifications}
                  onChange={handleNotificationsToggle}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-300 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-primary rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
              </label>
            </div>

            <div className="flex items-center justify-between p-4 opacity-50">
              <div className="flex items-center gap-3">
                <span className="material-symbols-outlined text-gray-600 dark:text-gray-400">
                  auto_awesome
                </span>
                <div>
                  <p className="text-gray-900 dark:text-white font-medium">
                    자동 검사 (MVP 이후)
                  </p>
                  <p className="text-gray-500 dark:text-gray-400 text-xs">
                    수신 메시지 자동 분석
                  </p>
                </div>
              </div>
              <label className="relative inline-flex items-center cursor-not-allowed">
                <input
                  type="checkbox"
                  checked={autoScan}
                  disabled
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-300 rounded-full peer peer-checked:bg-primary/50"></div>
              </label>
            </div>
          </div>
        </section>

        <section className="mb-6">
          <h3 className="text-gray-900 dark:text-white text-sm font-bold mb-3 px-2">
            데이터 관리
          </h3>
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 divide-y divide-gray-200 dark:divide-gray-700">
            <button
              onClick={handleClearHistory}
              className="flex items-center justify-between p-4 w-full text-left active:bg-gray-50 dark:active:bg-gray-700 transition-colors"
            >
              <div className="flex items-center gap-3">
                <span className="material-symbols-outlined text-danger">
                  delete
                </span>
                <div>
                  <p className="text-gray-900 dark:text-white font-medium">
                    검사 내역 삭제
                  </p>
                  <p className="text-gray-500 dark:text-gray-400 text-xs">
                    모든 검사 기록 제거
                  </p>
                </div>
              </div>
              <span className="material-symbols-outlined text-gray-400">
                chevron_right
              </span>
            </button>
          </div>
        </section>

        <section className="mb-6">
          <h3 className="text-gray-900 dark:text-white text-sm font-bold mb-3 px-2">
            정보
          </h3>
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 divide-y divide-gray-200 dark:divide-gray-700">
            <div className="flex items-center justify-between p-4">
              <div className="flex items-center gap-3">
                <span className="material-symbols-outlined text-gray-600 dark:text-gray-400">
                  info
                </span>
                <p className="text-gray-900 dark:text-white font-medium">
                  버전
                </p>
              </div>
              <p className="text-gray-500 dark:text-gray-400 text-sm">1.0.0</p>
            </div>

            <button 
              onClick={() => setShowPrivacyModal(true)}
              className="flex items-center justify-between p-4 w-full text-left active:bg-gray-50 dark:active:bg-gray-700 transition-colors"
            >
              <div className="flex items-center gap-3">
                <span className="material-symbols-outlined text-gray-600 dark:text-gray-400">
                  description
                </span>
                <p className="text-gray-900 dark:text-white font-medium">
                  개인정보 처리방침
                </p>
              </div>
              <span className="material-symbols-outlined text-gray-400">
                chevron_right
              </span>
            </button>
          </div>
        </section>

        <div className="bg-primary/5 dark:bg-primary/10 p-4 rounded-xl border border-primary/20">
          <div className="flex items-start gap-3">
            <span className="material-symbols-outlined text-primary text-xl">
              shield_locked
            </span>
            <div>
              <h4 className="text-primary dark:text-blue-300 font-bold mb-1">
                피싱체커 MVP
              </h4>
              <p className="text-gray-600 dark:text-gray-400 text-xs leading-relaxed">
                현재 수동 검사 모드로 운영 중입니다.
                MVP 이후 업데이트에서 자동 피싱 감지 기능이 추가될 예정입니다.
              </p>
            </div>
          </div>
        </div>
      </main>

      <BottomNav />

      {/* 개인정보 처리방침 모달 */}
      {showPrivacyModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-2xl max-w-md w-full p-6 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                개인정보 처리방침
              </h3>
              <button
                onClick={() => setShowPrivacyModal(false)}
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              >
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>
            
            <div className="space-y-4 text-sm text-gray-600 dark:text-gray-300 leading-relaxed">
              <p>
                본 앱은 사용자가 분석을 요청한 메시지 텍스트만 일시적으로 처리하며, 서버에 저장하지 않습니다.
              </p>
              <p>
                분석 결과 제공 후 원문 텍스트는 즉시 폐기됩니다.
              </p>
            </div>

            <button
              onClick={() => setShowPrivacyModal(false)}
              className="w-full mt-6 bg-primary text-white py-3 rounded-xl font-medium hover:bg-primary/90 transition-colors"
            >
              확인
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
