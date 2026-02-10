"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";

interface HeaderProps {
  title?: string;
  showBack?: boolean;
  showMenu?: boolean;
  showHistory?: boolean;
  rightAction?: React.ReactNode;
}

export default function Header({
  title = "피싱체커",
  showBack = false,
  showMenu = true,
  showHistory = false,
  rightAction,
}: HeaderProps) {
  const router = useRouter();

  return (
    <header className="flex items-center bg-background-light dark:bg-background-dark p-4 pb-2 justify-between sticky top-0 z-10">
      <div className="text-primary dark:text-gray-100 flex size-12 shrink-0 items-center justify-start">
        {showBack ? (
          <button onClick={() => router.back()} className="cursor-pointer">
            <span className="material-symbols-outlined">arrow_back_ios</span>
          </button>
        ) : showMenu ? (
          <span className="material-symbols-outlined text-primary dark:text-blue-400">shield_locked</span>
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
