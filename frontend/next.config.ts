import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: process.env.BUILD_TARGET === 'mobile' ? 'export' : undefined,
  images: {
    unoptimized: true,
  },
  trailingSlash: true, // Static Export 호환성
  // 외부 백엔드 API 사용
};

export default nextConfig;
