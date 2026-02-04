"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function BottomNav() {
  const pathname = usePathname();

  const isActive = (path: string) => pathname === path;

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-t border-gray-200 dark:border-gray-800 pb-6 pt-2 flex justify-around items-center">
      <Link
        href="/"
        className={`flex flex-col items-center gap-1 cursor-pointer ${
          isActive("/")
            ? "text-primary"
            : "opacity-50 grayscale hover:opacity-100 hover:grayscale-0"
        } transition-all`}
      >
        <span
          className={`material-symbols-outlined ${
            isActive("/") ? "font-bold" : ""
          }`}
        >
          home
        </span>
        <span className="text-[10px] font-medium">홈</span>
      </Link>
      <Link
        href="/history"
        className={`flex flex-col items-center gap-1 cursor-pointer ${
          isActive("/history")
            ? "text-primary"
            : "opacity-50 grayscale hover:opacity-100 hover:grayscale-0"
        } transition-all`}
      >
        <span className="material-symbols-outlined">history</span>
        <span className="text-[10px] font-medium">내역</span>
      </Link>
      <Link
        href="/settings"
        className={`flex flex-col items-center gap-1 cursor-pointer ${
          isActive("/settings")
            ? "text-primary"
            : "opacity-50 grayscale hover:opacity-100 hover:grayscale-0"
        } transition-all`}
      >
        <span className="material-symbols-outlined">settings</span>
        <span className="text-[10px] font-medium">설정</span>
      </Link>
    </nav>
  );
}
