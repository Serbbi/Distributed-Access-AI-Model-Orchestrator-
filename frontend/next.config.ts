import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  webpack: (config) => {
    config.externals = config.externals || [];
    config.externals.push("node:inspector/promises");
    return config;
  },
};

export default nextConfig;
