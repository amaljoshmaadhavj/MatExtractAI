/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  // Server configuration for development
  devIndicators: {
    buildActivity: true,
  },
  // Ensure consistent port handling
  reactStrictMode: true,
}

export default nextConfig
