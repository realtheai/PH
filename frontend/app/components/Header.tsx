"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";

interface HeaderProps {
  title?: string;
  showBack?: boolean;
  showMenu?: boolean;
  showHistory?: boolean;
  rightAction?: React.ReactNode;
  onBack?: () => void; // 커스텀 뒤로가기 동작
  onMenuClick?: () => void; // 메뉴 아이콘 클릭 동작
}

export default function Header({
  title = "피싱체커",
  showBack = false,
  showMenu = true,
  showHistory = false,
  rightAction,
  onBack,
  onMenuClick,
}: HeaderProps) {
  const router = useRouter();

  const handleBack = () => {
    if (onBack) {
      onBack(); // 커스텀 뒤로가기 동작
    } else {
      router.back(); // 기본 뒤로가기
    }
  };

  return (
    <header className="flex items-center bg-background-light dark:bg-background-dark p-4 pb-2 justify-between sticky top-0 z-10">
      <div className="text-primary dark:text-gray-100 flex size-12 shrink-0 items-center justify-start">
        {showBack ? (
          <button onClick={handleBack} className="cursor-pointer">
            <span className="material-symbols-outlined">arrow_back_ios</span>
          </button>
        ) : showMenu ? (
          onMenuClick ? (
            <button onClick={onMenuClick} className="cursor-pointer">
              <span className="material-symbols-outlined text-primary dark:text-blue-400">refresh</span>
            </button>
          ) : (
            <span className="material-symbols-outlined text-primary dark:text-blue-400">shield_locked</span>
          )
        ) : (
          <div className="w-6" />
        )}
      </div>
      <h2 className="text-primary dark:text-white text-lg font-bold leading-tight tracking-[-0.015em] flex-1 text-center">
        {title}
      </h2>
      <div className="flex w-12 items-center justify-end">
        {rightAction ? (
          rightAction
        ) : showHistory ? (
          <Link
            href="/history"
            className="text-primary dark:text-gray-300 text-sm font-bold leading-normal tracking-[0.015em] cursor-pointer"
          >
            내역
          </Link>
        ) : (
          <div className="w-6" />
        )}
      </div>
    </header>
  );
}
