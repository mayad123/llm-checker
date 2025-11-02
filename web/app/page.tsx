"use client";
import React, { useState } from "react";

type Claim = {
  text: string;
  verdict: "supported" | "contradicted" | "unclear";
  confidence: number;
  citation?: { url: string; snippet: string };
};

export default function Page() {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [claims, setClaims] = useState<Claim[]>([]);
  const [checkedOn, setCheckedOn] = useState<string>("");
  const [error, setError] = useState<string>("");
  const [expandedClaim, setExpandedClaim] = useState<number | null>(null);

  async function runCheck() {
    if (!input.trim()) {
      setError("Please paste an LLM response to check");
      return;
    }
    setLoading(true);
    setError("");
    setClaims([]);
    setCheckedOn("");
    try {
      // Use environment variable for API URL, fallback to /api/check for local dev
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "/api/check";
      const res = await fetch(apiUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ llm_output: input, debug: true }),
      });
      
      if (!res.ok) {
        throw new Error(`Failed to check: ${res.statusText}`);
      }
      
      const data = await res.json();
      setCheckedOn(data.checked_on);
      setClaims(data.claims || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
      runCheck();
    }
  };

  const chipStyles = (v: Claim["verdict"]) => {
    const base = "inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold transition-all duration-200";
    return v === "supported"
      ? `${base} bg-green-50 text-green-700 border border-green-200 shadow-sm`
      : v === "contradicted"
      ? `${base} bg-red-50 text-red-700 border border-red-200 shadow-sm`
      : `${base} bg-amber-50 text-amber-700 border border-amber-200 shadow-sm`;
  };

  const getVerdictIcon = (v: Claim["verdict"]) => {
    if (v === "supported") return "✓";
    if (v === "contradicted") return "✗";
    return "?";
  };

  const getConfidenceColor = (conf: number) => {
    if (conf >= 0.7) return "text-green-600";
    if (conf >= 0.4) return "text-amber-600";
    return "text-red-600";
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      <main className="max-w-5xl mx-auto px-4 py-8 md:py-12">
        {/* Header */}
        <div className="text-center mb-10 space-y-3">
          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent">
            LLM Fact Checker
          </h1>
          <p className="text-slate-600 text-lg max-w-2xl mx-auto">
            Paste responses from ChatGPT, Claude, or any LLM and get instant fact-checking with verified sources
          </p>
        </div>

        {/* Input Card */}
        <div className="bg-white rounded-2xl shadow-xl p-6 md:p-8 mb-8 border border-slate-200 transition-all duration-300 hover:shadow-2xl">
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="block text-sm font-semibold text-slate-700">
                Paste LLM Response (ChatGPT, Claude, etc.)
              </label>
              <p className="text-xs text-slate-500">
                Copy and paste any response from ChatGPT, Claude, Gemini, or other LLMs to fact-check claims and see verified sources
              </p>
            </div>
            <textarea
              className="w-full min-h-[200px] p-4 border-2 border-slate-200 rounded-xl focus:border-blue-500 focus:ring-4 focus:ring-blue-100 outline-none transition-all duration-200 resize-none text-slate-700 font-medium placeholder:text-slate-400"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Paste your LLM response here...&#10;&#10;Example: &#10;Ali Ghodsi has been the CEO of Databricks since 2016. The company was founded in 2013 and is known for its data analytics platform."
            />
            <div className="flex items-center justify-between">
              <p className="text-xs text-slate-500">
                Press <kbd className="px-2 py-1 bg-slate-100 rounded text-xs font-mono">Ctrl/Cmd + Enter</kbd> to check
              </p>
              <button
                onClick={runCheck}
                disabled={loading || !input.trim()}
                className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-105 active:scale-95 flex items-center gap-2"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>Checking...</span>
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span>Check Facts</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border-2 border-red-200 rounded-xl p-4 mb-6 animate-slide-down">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <p className="text-red-700 font-medium">{error}</p>
            </div>
          </div>
        )}

        {/* Results Header */}
        {checkedOn && (
          <div className="mb-6 flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-3">
              <div className="h-1 w-12 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full"></div>
              <p className="text-sm text-slate-600 font-medium">
                Checked on <span className="text-slate-900 font-semibold">{checkedOn}</span>
              </p>
            </div>
            {claims.length > 0 && (
              <div className="px-4 py-2 bg-slate-100 rounded-full">
                <span className="text-sm font-semibold text-slate-700">
                  {claims.length} {claims.length === 1 ? "claim" : "claims"} found
                </span>
              </div>
            )}
          </div>
        )}

        {/* Claims Results */}
        {claims.length > 0 && (
          <div className="space-y-4 animate-fade-in">
            {claims.map((c, i) => (
              <div
                key={i}
                className="bg-white rounded-xl shadow-lg border-2 border-slate-100 overflow-hidden transition-all duration-300 hover:shadow-xl hover:border-slate-200"
              >
                <div className="p-6">
                  <div className="flex items-start justify-between gap-4 mb-4">
                    <div className="flex-1">
                      <p className="text-slate-800 font-medium leading-relaxed text-lg">
                        {c.text}
                      </p>
                    </div>
                    <div className="flex flex-col items-end gap-2">
                      <span className={chipStyles(c.verdict)}>
                        <span className="text-base">{getVerdictIcon(c.verdict)}</span>
                        <span className="capitalize">{c.verdict}</span>
                      </span>
                      <div className="flex items-center gap-2">
                        <span className={`text-xs font-semibold ${getConfidenceColor(c.confidence)}`}>
                          {Math.round(c.confidence * 100)}% confidence
                        </span>
                        <div className="w-16 h-1.5 bg-slate-200 rounded-full overflow-hidden">
                          <div
                            className={`h-full transition-all duration-500 ${
                              c.confidence >= 0.7
                                ? "bg-green-500"
                                : c.confidence >= 0.4
                                ? "bg-amber-500"
                                : "bg-red-500"
                            }`}
                            style={{ width: `${c.confidence * 100}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {c.citation && (
                    <div className="mt-4 pt-4 border-t border-slate-200">
                      <button
                        onClick={() => setExpandedClaim(expandedClaim === i ? null : i)}
                        className="w-full flex items-center justify-between text-left group"
                      >
                        <span className="text-sm font-semibold text-blue-600 group-hover:text-blue-700 transition-colors">
                          {expandedClaim === i ? "Hide Evidence" : "View Evidence"}
                        </span>
                        <svg
                          className={`w-5 h-5 text-blue-600 transition-transform duration-200 ${
                            expandedClaim === i ? "rotate-180" : ""
                          }`}
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </button>

                      {expandedClaim === i && (
                        <div className="mt-4 p-4 bg-slate-50 rounded-lg border border-slate-200 animate-slide-down">
                          <div className="space-y-3">
                            <div>
                              <p className="text-xs font-semibold text-slate-500 mb-2">EVIDENCE SNIPPET</p>
                              <p className="text-sm text-slate-700 leading-relaxed italic">
                                "{c.citation.snippet}"
                              </p>
                            </div>
                            <div>
                              <p className="text-xs font-semibold text-slate-500 mb-2">SOURCE</p>
                              <a
                                href={c.citation.url}
                                target="_blank"
                                rel="noreferrer"
                                className="text-blue-600 hover:text-blue-700 underline break-all text-sm font-medium flex items-center gap-2 group"
                              >
                                <span>{c.citation.url}</span>
                                <svg className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                </svg>
                              </a>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Empty State */}
        {!loading && claims.length === 0 && checkedOn && (
          <div className="text-center py-12 bg-white rounded-xl shadow-lg border border-slate-200">
            <svg className="w-16 h-16 mx-auto text-slate-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p className="text-slate-600 font-medium mb-2">No claims found to verify</p>
            <p className="text-sm text-slate-500">The LLM response may not contain verifiable factual claims.</p>
          </div>
        )}

        {/* Help Section - Only show when no results */}
        {!loading && claims.length === 0 && !checkedOn && (
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-6 mb-8">
            <div className="flex items-start gap-3">
              <svg className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
              <div className="space-y-2 flex-1">
                <h3 className="text-sm font-semibold text-blue-900">How to use:</h3>
                <ol className="text-sm text-blue-800 space-y-1 list-decimal list-inside">
                  <li>Copy a response from ChatGPT, Claude, Gemini, or any other LLM</li>
                  <li>Paste it in the text area above</li>
                  <li>Click "Check Facts" to see verified sources and fact-checking results</li>
                </ol>
                <p className="text-xs text-blue-700 mt-3">
                  <strong>Note:</strong> This tool analyzes factual claims in the text and verifies them against online sources. It does not call ChatGPT or any LLM—you provide the response to check.
                </p>
              </div>
            </div>
          </div>
        )}
      </main>

      <style jsx>{`
        @keyframes slide-down {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        @keyframes fade-in {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }
        .animate-slide-down {
          animation: slide-down 0.3s ease-out;
        }
        .animate-fade-in {
          animation: fade-in 0.5s ease-out;
        }
      `}</style>
    </div>
  );
}
