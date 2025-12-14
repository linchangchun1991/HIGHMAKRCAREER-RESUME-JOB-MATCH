/** @type {import('next').NextConfig} */
const nextConfig = {
  // 确保服务器端可以处理 Node.js 模块
  webpack: (config, { isServer }) => {
    if (isServer) {
      config.externals = config.externals || []
      // pdf-parse 需要特殊处理
      config.externals.push({
        canvas: "commonjs canvas",
      })
    }
    return config
  },
  // 增加 API 路由超时时间
  experimental: {
    serverActions: {
      bodySizeLimit: "10mb",
    },
  },
  // 图片优化配置
  images: {
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },
}

module.exports = nextConfig
