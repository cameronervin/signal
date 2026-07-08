import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  typescript: {
    ignoreBuildErrors: false
  },
  turbopack: {
    root: "/Users/cameronervin/Documents/projects/signal"
  }
};

export default nextConfig;
