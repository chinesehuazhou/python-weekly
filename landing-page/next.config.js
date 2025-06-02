const createNextIntlPlugin = require('next-intl/plugin');

const withNextIntl = createNextIntlPlugin('./i18n/request.ts');

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export', // 启用静态导出
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  // 确保静态资源路径正确
  assetPrefix: process.env.NODE_ENV === 'production' ? '' : '',
  experimental: {
    optimizeCss: true,
    optimizePackageImports: ['react-icons', 'framer-motion'],
  },
  // 移除turbopack配置，因为我们已经在package.json中移除了--turbo参数
  // 如果需要启用turbopack，可以使用以下配置
  // turbopack: {}
};

module.exports = withNextIntl(nextConfig);