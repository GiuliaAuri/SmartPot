import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:5000/api",
  },
  // Ensure environment variables are available at build time
  publicRuntimeConfig: {
    apiUrl: process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:5000/api",
  },
  // Allow cross-origin requests from localhost and 127.0.0.1
  allowedDevOrigins: [
    "127.0.0.1",
    "localhost",
    "127.0.0.1:3000",
    "localhost:3000",
    "127.0.0.1:5000",
    "localhost:5000"
  ],
};

export default nextConfig;
