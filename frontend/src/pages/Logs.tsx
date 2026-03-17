import { useEffect, useState, useRef } from "react";
import { fetchLogs } from "../lib/api";

type LogEntry = string | { ts?: number; level?: string; name?: string; msg?: string };

function formatLogEntry(entry: LogEntry): string {
  if (typeof entry === "string") return entry;
  if (entry && typeof entry === "object" && "msg" in entry) return String(entry.msg ?? "");
  return String(entry);
}

export default function Logs() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const preRef = useRef<HTMLPreElement>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchLogs();
      setLogs(data.logs ?? []);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to fetch logs");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    const interval = setInterval(load, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (preRef.current) preRef.current.scrollTop = preRef.current.scrollHeight;
  }, [logs]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-foreground">Logs</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Recent application logs (refreshes every 5s)
          </p>
        </div>
        <button
          type="button"
          onClick={load}
          disabled={loading}
          className="rounded-lg px-4 py-2 text-sm font-medium bg-muted text-foreground hover:bg-muted/80 disabled:opacity-50 transition-colors"
        >
          Refresh
        </button>
      </div>

      {error && (
        <div className="rounded-lg bg-danger/10 border border-danger/20 px-4 py-3 text-danger text-sm">
          {error}
        </div>
      )}

      <div className="rounded-xl border border-border bg-card shadow-sm overflow-hidden">
        <pre
          ref={preRef}
          className="block p-4 h-[60vh] overflow-auto text-sm text-muted-foreground font-mono whitespace-pre-wrap break-words"
        >
          {loading && logs.length === 0 ? (
            <span className="text-muted-foreground">Loading logs…</span>
          ) : logs.length === 0 ? (
            <span className="text-muted-foreground">No logs yet.</span>
          ) : (
            logs.map(formatLogEntry).join("\n")
          )}
        </pre>
      </div>
    </div>
  );
}
