import { useEffect, useState } from "react"
import { Check, Send, X } from "lucide-react"

type Item = {
  id: number
  status: string
  repo_id: string
  campaign: string
  status_text: string
}

export default function OutboxPage() {
  const [items, setItems] = useState<Item[]>([])
  const [msg, setMsg] = useState("")

  const load = () =>
    fetch("/api/v1/outbox")
      .then((r) => r.json())
      .then((d) => setItems(d.items || []))

  useEffect(() => {
    load()
    const t = setInterval(load, 5000)
    return () => clearInterval(t)
  }, [])

  const act = async (id: number, path: string) => {
    const r = await fetch(`/api/v1/outbox/${id}/${path}`, { method: "POST" })
    const j = await r.json()
    setMsg(j.message || j.error || JSON.stringify(j))
    load()
  }

  return (
    <div className="p-6 max-w-3xl">
      <h1 className="text-xl font-semibold mb-1">Outbox</h1>
      <p className="text-sm text-zinc-500 mb-4">
        Fleet-PR drafts land here. Approve, then publish (dry-run until MASTODON_DRY_RUN=0).
      </p>
      {msg && <p className="text-sm text-violet-300 mb-3">{msg}</p>}
      <div className="space-y-3">
        {items.map((it) => (
          <div key={it.id} className="border border-zinc-800 bg-zinc-900 rounded-lg p-4">
            <div className="flex justify-between text-sm mb-2">
              <span>
                #{it.id} <span className="text-zinc-400">{it.repo_id}</span> · {it.status}
              </span>
              <span className="text-zinc-600">{it.campaign}</span>
            </div>
            <pre className="text-sm whitespace-pre-wrap text-zinc-300 mb-3">{it.status_text}</pre>
            <div className="flex gap-2">
              <button
                onClick={() => act(it.id, "approve")}
                disabled={it.status === "approved" || it.status === "published"}
                className="flex items-center gap-1 px-2.5 py-1.5 text-sm rounded bg-emerald-700/80 disabled:opacity-40"
              >
                <Check size={14} /> Approve
              </button>
              <button
                onClick={() => act(it.id, "publish")}
                disabled={it.status !== "approved"}
                className="flex items-center gap-1 px-2.5 py-1.5 text-sm rounded border border-violet-500/40 text-violet-300 disabled:opacity-40"
              >
                <Send size={14} /> Publish
              </button>
              <button
                onClick={() => act(it.id, "reject")}
                disabled={it.status === "published"}
                className="flex items-center gap-1 px-2.5 py-1.5 text-sm rounded border border-zinc-700 text-zinc-400 disabled:opacity-40"
              >
                <X size={14} /> Reject
              </button>
            </div>
          </div>
        ))}
        {items.length === 0 && <p className="text-sm text-zinc-600">Empty — queue from fleet-PR Drafts.</p>}
      </div>
    </div>
  )
}
