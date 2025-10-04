"use client";
import React, { useState } from "react";

type Claim = {
  text: string;
  verdict: "supported" | "contradicted" | "unclear";
  confidence: number;
  citation?: { url: string; snippet: string };
};

export default function Page() {
  const [input, setInput] = useState(
    "Ali Ghodsi is the CEO of Databricks since 2016."
  );
  const [loading, setLoading] = useState(false);
  const [claims, setClaims] = useState<Claim[]>([]);
  const [checkedOn, setCheckedOn] = useState<string>("");

  async function runCheck() {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/check", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ llm_output: input }),
      });
      const data = await res.json();
      setCheckedOn(data.checked_on);
      setClaims(data.claims || []);
    } finally {
      setLoading(false);
    }
  }

  const chip = (v: Claim["verdict"]) =>
    v === "supported" ? "bg-green-100 text-green-800" :
    v === "contradicted" ? "bg-red-100 text-red-800" :
    "bg-gray-100 text-gray-800";

  return (
    <main className="max-w-3xl mx-auto p-6 space-y-4">
      <h1 className="text-2xl font-semibold">LLM Fact Check (MVP)</h1>
      <textarea
        className="w-full h-36 p-3 border rounded-md"
        value={input}
        onChange={(e) => setInput(e.target.value)}
      />
      <button
        onClick={runCheck}
        disabled={loading}
        className="px-4 py-2 rounded-md bg-black text-white disabled:opacity-50"
      >
        {loading ? "Checking..." : "Check"}
      </button>

      {checkedOn && <p className="text-sm text-gray-500">Checked on {checkedOn}</p>}

      <div className="space-y-3">
        {claims.map((c, i) => (
          <div key={i} className="border rounded-md p-3">
            <div className="flex items-center justify-between">
              <p className="font-medium">{c.text}</p>
              <span className={`text-xs px-2 py-1 rounded ${chip(c.verdict)}`}>
                {c.verdict} • {c.confidence.toFixed(2)}
              </span>
            </div>
            {c.citation && (
              <details className="mt-2">
                <summary className="cursor-pointer text-sm underline">
                  View evidence
                </summary>
                <div className="mt-2 text-sm">
                  <p className="italic">“{c.citation.snippet}”</p>
                  <a
                    href={c.citation.url}
                    target="_blank"
                    className="text-blue-600 underline break-all"
                    rel="noreferrer"
                  >
                    {c.citation.url}
                  </a>
                </div>
              </details>
            )}
          </div>
        ))}
      </div>
    </main>
  );
}
