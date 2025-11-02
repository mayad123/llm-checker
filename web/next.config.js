/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'export',
  images: {
    unoptimized: true,
  },
  // For GitHub Pages, update basePath if your repo name is not the root
  // basePath: process.env.NODE_ENV === 'production' ? '/your-repo-name' : '',
  // assetPrefix: process.env.NODE_ENV === 'production' ? '/your-repo-name' : '',
  trailingSlash: true,
};

module.exports = nextConfig;
