import { useEffect, useState } from "react"

export default function Accounts() {
  const [health, setHealth] = useState<any>(null)
  useEffect(() => {
    fetch("/api/health")
      .then((r) => r.json())
      .then(setHealth)
  }, [])
  return (
    <div className="p-6 max-w-xl">
      <h1 className="text-xl font-semibold mb-4">Accounts</h1>
      <div className="border border-zinc-800 bg-zinc-900 rounded-lg p-4 text-sm space-y-2">
        <div>Instance configured: {health?.instance_configured ? "yes" : "no"}</div>
        <div>Dry run: {String(health?.dry_run)}</div>
        <div className="text-zinc-500">Multi-account profiles: planned v0.2</div>
      </div>
    </div>
  )
}
