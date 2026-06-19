import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import { BrowserRouter, Routes, Route } from "react-router"

import "./index.css"
import App from "./App.tsx"
import ServerDevdocs from "./site/development/Server.tsx"

import { Devbar } from "./components/dev.tsx"
import ThemeDisplay from "./site/development/Theme.tsx"


createRoot(document.getElementById("root")!).render(
  <StrictMode>

    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/check" element={<p>checking...</p>} />

        <Route path="/dev/server" element={<ServerDevdocs />} />
        <Route path="/dev/theme" element={<ThemeDisplay />} />
      </Routes>
    </BrowserRouter>

    {import.meta.env.DEV && <Devbar />}
  </StrictMode>,
)
