/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  },
  experimental: {
    esmExternals: "loose", // allow ESM-only packages like react-markdown
  },
}

module.exports = nextConfig

