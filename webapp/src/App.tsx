import { NavLink, Route, Routes } from "react-router-dom"
import clsx from "clsx"
import { Inbox, PenSquare, Radio, Settings, Users } from "lucide-react"
import Compose from "./pages/Compose"
import OutboxPage from "./pages/Outbox"
import Timelines from "./pages/Timelines"
import Accounts from "./pages/Accounts"
import SettingsPage from "./pages/Settings"

const NAV = [
  { to: "/", label: "Outbox", icon: Inbox },
  { to: "/compose", label: "Compose", icon: PenSquare },
  { to: "/timelines", label: "Timelines", icon: Radio },
  { to: "/accounts", label: "Accounts", icon: Users },
  { to: "/settings", label: "Settings", icon: Settings },
]

export default function App() {
  return (
    <div className="flex h-screen bg-zinc-950 text-zinc-100">
      <aside className="w-48 border-r border-zinc-800 bg-zinc-900 flex flex-col">
        <div className="px-3 py-4 border-b border-zinc-800 font-semibold text-violet-400 text-sm tracking-wide">
          Mastodon MCP
        </div>
        <nav className="flex-1 p-2 space-y-0.5">
          {NAV.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) =>
                clsx(
                  "flex items-center gap-2 px-2.5 py-2 rounded-md text-sm",
                  isActive ? "bg-violet-500/20 text-violet-300" : "text-zinc-400 hover:bg-zinc-800",
                )
              }
            >
              <Icon size={16} />
              {label}
            </NavLink>
          ))}
        </nav>
        <p className="text-[11px] text-zinc-600 px-3 pb-3">dry-run default · human approve</p>
      </aside>
      <main className="flex-1 overflow-y-auto">
        <Routes>
          <Route path="/" element={<OutboxPage />} />
          <Route path="/compose" element={<Compose />} />
          <Route path="/timelines" element={<Timelines />} />
          <Route path="/accounts" element={<Accounts />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </main>
    </div>
  )
}
