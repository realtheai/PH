import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'export',
  images: {
    unoptimized: true,
  },
  // API 라우트는 static export에서 사용 불가하므로
  // 외부 백엔드 API 사용
};

export default nextConfig;
