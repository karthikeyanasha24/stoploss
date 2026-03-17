import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchSettings, saveSettings, uploadCredentials, syncSheetToDb } from "../lib/api";
import type { Settings } from "../lib/api";

export default function Settings() {
  const navigate = useNavigate();
  const [data, setData] = useState<Settings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [credError, setCredError] = useState<string | null>(null);
  const [syncing, setSyncing] = useState(false);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const s = await fetchSettings();
        if (!cancelled) setData(s);
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : "Failed to load settings");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, []);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!data) return;
    setSaving(true);
    setError(null);
    setSuccess(null);
    try {
      await saveSettings({
        API_PROVIDER: "tradier",
        API_KEY: data.API_KEY === "********" ? undefined : data.API_KEY,
        SPREADSHEET_ID: data.SPREADSHEET_ID,
        GOOGLE_CREDENTIALS_PATH: data.GOOGLE_CREDENTIALS_PATH,
        POLLING_INTERVAL: data.POLLING_INTERVAL,
        MARKET_TIMEZONE: data.MARKET_TIMEZONE,
        MARKET_OPEN: data.MARKET_OPEN,
        MARKET_CLOSE: data.MARKET_CLOSE,
        ANALYSIS_DAYS: data.ANALYSIS_DAYS,
        MOCK_API: data.MOCK_API,
        PAPER_TRADING: data.PAPER_TRADING,
      });
      setSuccess("Settings saved. Changes applied. Redirecting to Dashboard…");
      const updated = await fetchSettings();
      setData(updated);
      window.dispatchEvent(new CustomEvent("settings-saved"));
      setTimeout(() => navigate("/"), 1000);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to save settings");
    } finally {
      setSaving(false);
    }
  }

  async function handleSyncNow() {
    setSyncing(true);
    setError(null);
    setSuccess(null);
    try {
      const res = await syncSheetToDb();
      if (res.ok) {
        setSuccess(`Synced: ${res.added ?? 0} new trades added. Dashboard updated.`);
        window.dispatchEvent(new CustomEvent("settings-saved"));
      } else {
        setError(res.error ?? "Sync failed");
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Sync failed");
    } finally {
      setSyncing(false);
    }
  }

  async function handleCredUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setCredError(null);
    try {
      await uploadCredentials(file);
      setSuccess("Credentials uploaded.");
    } catch (err) {
      setCredError(err instanceof Error ? err.message : "Failed to upload");
    }
    e.target.value = "";
  }

  const inputClass =
    "block w-full rounded-lg border border-border bg-background px-3 py-2 text-foreground placeholder:text-muted-foreground focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent";
  const labelClass = "block text-sm font-medium text-foreground mb-1";

  if (loading || !data) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-semibold">Settings</h1>
        <div className="rounded-xl border border-border bg-card p-8 animate-pulse">
          <div className="h-8 w-48 rounded bg-muted mb-6" />
          <div className="space-y-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-10 rounded bg-muted" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold text-foreground">Settings</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          API, spreadsheet, and market configuration
        </p>
      </div>

      {error && (
        <div className="rounded-lg bg-danger/10 border border-danger/20 px-4 py-3 text-danger text-sm">
          {error}
        </div>
      )}
      {success && (
        <div className="rounded-lg bg-success/10 border border-success/20 px-4 py-3 text-success text-sm">
          {success}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="rounded-xl border border-border bg-card shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-border">
            <h2 className="text-lg font-semibold text-foreground">API & Spreadsheet</h2>
          </div>
          <div className="p-6 space-y-4">
            <div>
              <label className={labelClass}>API Provider</label>
              <input
                type="text"
                value="Tradier"
                readOnly
                disabled
                className={`${inputClass} cursor-not-allowed opacity-80 bg-muted/50`}
              />
            </div>
            {data.API_PROVIDER === "tradier" && (
              <div className="flex items-center gap-2">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={data.PAPER_TRADING ?? true}
                    onChange={(e) => setData({ ...data, PAPER_TRADING: e.target.checked })}
                    className="rounded border-border"
                  />
                  <span className="text-sm font-medium text-foreground">Paper Trading (Sandbox)</span>
                </label>
                <span className="text-xs text-muted-foreground">Use sandbox API for testing</span>
              </div>
            )}
            <div>
              <label className={labelClass}>API Key / Token</label>
              <input
                type="password"
                value={data.API_KEY}
                onChange={(e) => setData({ ...data, API_KEY: e.target.value })}
                placeholder="Leave blank to keep current"
                className={inputClass}
              />
            </div>
            <div>
              <label className={labelClass}>Spreadsheet ID</label>
              <input
                type="text"
                value={data.SPREADSHEET_ID}
                onChange={(e) => setData({ ...data, SPREADSHEET_ID: e.target.value })}
                className={inputClass}
              />
            </div>
            <div>
              <label className={labelClass}>Google Credentials Path</label>
              <input
                type="text"
                value={data.GOOGLE_CREDENTIALS_PATH}
                onChange={(e) => setData({ ...data, GOOGLE_CREDENTIALS_PATH: e.target.value })}
                className={inputClass}
              />
              <div className="mt-2 flex flex-wrap gap-2">
                <label className="inline-flex items-center gap-2 rounded-lg border border-border bg-muted/30 px-4 py-2 text-sm cursor-pointer hover:bg-muted/50 transition-colors">
                  <input type="file" accept=".json" onChange={handleCredUpload} className="hidden" />
                  Upload credentials.json
                </label>
                <button
                  type="button"
                  onClick={handleSyncNow}
                  disabled={syncing}
                  className="rounded-lg border border-border bg-sky-500/20 text-sky-600 dark:text-sky-400 px-4 py-2 text-sm font-medium hover:bg-sky-500/30 disabled:opacity-50 transition-colors"
                >
                  {syncing ? "Syncing…" : "Sync sheet to Dashboard"}
                </button>
              </div>
              <p className="mt-1 text-xs text-muted-foreground">If Dashboard shows 0 trades but Sheet Reference works, click &quot;Sync sheet to Dashboard&quot; to load trades.</p>
              {credError && <p className="mt-1 text-sm text-danger">{credError}</p>}
            </div>
          </div>
        </div>

        <div className="rounded-xl border border-border bg-card shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-border">
            <h2 className="text-lg font-semibold text-foreground">Market & Analysis</h2>
          </div>
          <div className="p-6 space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className={labelClass}>Market Timezone</label>
                <input
                  type="text"
                  value={data.MARKET_TIMEZONE}
                  onChange={(e) => setData({ ...data, MARKET_TIMEZONE: e.target.value })}
                  className={inputClass}
                />
              </div>
              <div>
                <label className={labelClass}>Polling Interval (seconds)</label>
                <input
                  type="number"
                  value={data.POLLING_INTERVAL}
                  onChange={(e) => setData({ ...data, POLLING_INTERVAL: parseInt(e.target.value, 10) || 300 })}
                  className={inputClass}
                />
              </div>
              <div>
                <label className={labelClass}>Market Open</label>
                <input
                  type="text"
                  value={data.MARKET_OPEN}
                  onChange={(e) => setData({ ...data, MARKET_OPEN: e.target.value })}
                  placeholder="09:30"
                  className={inputClass}
                />
              </div>
              <div>
                <label className={labelClass}>Market Close</label>
                <input
                  type="text"
                  value={data.MARKET_CLOSE}
                  onChange={(e) => setData({ ...data, MARKET_CLOSE: e.target.value })}
                  placeholder="16:00"
                  className={inputClass}
                />
              </div>
              <div>
                <label className={labelClass}>Analysis Days</label>
                <input
                  type="number"
                  value={data.ANALYSIS_DAYS}
                  onChange={(e) => setData({ ...data, ANALYSIS_DAYS: parseInt(e.target.value, 10) || 7 })}
                  className={inputClass}
                />
              </div>
              <div className="flex flex-col gap-2 sm:col-span-2">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={data.MOCK_API}
                    onChange={(e) => setData({ ...data, MOCK_API: e.target.checked })}
                    className="rounded border-border"
                  />
                  <span className="text-sm font-medium text-foreground">Mock API</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <button
          type="submit"
          disabled={saving}
          className="rounded-lg px-6 py-2.5 text-sm font-medium bg-accent text-accent-foreground hover:opacity-90 disabled:opacity-50 transition-opacity"
        >
          {saving ? "Saving…" : "Save Settings"}
        </button>
      </form>
    </div>
  );
}
