import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  // Backend thuần API: không có trang nào, không cần tối ưu ảnh/font.
  reactStrictMode: true,
  poweredByHeader: false,
  serverExternalPackages: ['@neondatabase/serverless'],
}

export default nextConfig
