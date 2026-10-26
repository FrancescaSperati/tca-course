import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// The browser only talks to Vite; /api/* is forwarded to FastAPI (no CORS needed).
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
