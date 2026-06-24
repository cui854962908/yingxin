import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"
import { fileURLToPath, URL } from "node:url"

const campusRoot = fileURLToPath(new URL(".", import.meta.url))

export default defineConfig({
  root: campusRoot,
  base: "./",
  plugins: [react()],
  publicDir: "static",
  server: {
    host: "0.0.0.0",
    port: 5173,
    strictPort: true,
  },
  preview: {
    host: "0.0.0.0",
    port: 5173,
    strictPort: true,
  },
  build: {
    outDir: "../public/campus",
    emptyOutDir: true,
    sourcemap: false,
    rollupOptions: {
      input: fileURLToPath(new URL("./app.html", import.meta.url)),
    },
  },
})
