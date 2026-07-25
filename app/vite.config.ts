import { defineConfig } from "vite"
import { execSync } from "node:child_process"
import react from "@vitejs/plugin-react"

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  define: {
    __BUILD_TIME__: JSON.stringify(new Date().toISOString()),

    __CONFIG__: JSON.parse(execSync(
      "uv run --directory .. cli project dump-config"
    ).toString()),

    __PROJECT__: JSON.parse(execSync(
      "uv run --directory .. cli project status"
    ).toString()),
  }
})
