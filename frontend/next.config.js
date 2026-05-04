/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "https://rentalme-backend.sklshk.easypanel.host/api/:path*",
      },
    ];
  },
};

module.exports = nextConfig;
