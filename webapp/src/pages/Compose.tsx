import { useState } from "react"

export default function Compose() {
  const [text, setText] = useState("")
  const [result, setResult] = useState("")

  const enqueue = async () => {
    const r = await fetch("/api/v1/outbox", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        status_text: text,
        source: "compose-ui",
        repo_id: "manual",
      }),
    })
    setResult(JSON.stringify(await r.json(), null, 2))
    setText("")
  }

  return (
    <div className="p-6 max-w-2xl">
      <h1 className="text-xl font-semibold mb-1">Compose</h1>
      <p className="text-sm text-zinc-500 mb-4">Enqueues to outbox — does not post directly.</p>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={6}
        className="w-full bg-zinc-950 border border-zinc-700 rounded-md p-3 text-sm mb-3"
        placeholder="Useful pointer, not hype…"
      />
      <button
        onClick={enqueue}
        disabled={!text.trim()}
        className="px-3 py-2 text-sm rounded-md bg-violet-600 hover:bg-violet-500 disabled:opacity-40"
      >
        Enqueue to outbox
      </button>
      {result && <pre className="mt-4 text-xs text-zinc-500 whitespace-pre-wrap">{result}</pre>}
    </div>
  )
}
