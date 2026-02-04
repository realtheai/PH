import type { Metadata } from "next";
import { Public_Sans } from "next/font/google";
import "./globals.css";

const publicSans = Public_Sans({
  variable: "--font-public-sans",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "피싱체커 - 스미싱 탐지 앱",
  description: "의심 메시지를 즉시 검사하고 피싱으로부터 안전하게 보호하세요",
  keywords: ["피싱", "스미싱", "보안", "사기", "탐지"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko" className="light">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap"
          rel="stylesheet"
        />
      </head>
      <body
        className={`${publicSans.variable} bg-background-light dark:bg-background-dark text-gray-900 dark:text-gray-100 antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
