import { useEffect, useState } from "react"

export default function SettingsPage() {
  const [health, setHealth] = useState<any>(null)
  useEffect(() => {
    fetch("/api/health")
      .then((r) => r.json())
      .then(setHealth)
  }, [])
  return (
    <div className="p-6 max-w-xl">
      <h1 className="text-xl font-semibold mb-4">Settings</h1>
      <pre className="text-sm bg-zinc-900 border border-zinc-800 rounded p-4 whitespace-pre-wrap">
        {JSON.stringify(health, null, 2)}
      </pre>
      <p className="text-sm text-zinc-500 mt-3">
        Edit <code className="text-zinc-400">.env</code>: MASTODON_INSTANCE, MASTODON_ACCESS_TOKEN,
        MASTODON_DRY_RUN (default 1).
      </p>
    </div>
  )
}
