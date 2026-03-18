import { useEffect, useState, useMemo, useCallback } from "react";
import { Link } from "react-router-dom";
import { fetchTrades, fetchAnalysis, syncSheetToDb } from "../lib/api";
import type { Trade } from "../lib/api";

type SortKey =
  | "entry_time"
  | "ticker"
  | "strike_price"
  | "option_type"
  | "expiry_date"
  | "entry_price"
  | "drawdown_price"
  | "current_price"
  | "analyst_name"
  | "status"
  | "max_drawdown_percent";
type SortDir = "asc" | "desc";

const PAGE_SIZE = 10;

function SkeletonCard() {
  return (
    <div className="rounded-xl border border-border bg-card p-6 animate-pulse">
      <div className="h-4 w-24 rounded bg-muted mb-3" />
      <div className="h-8 w-16 rounded bg-muted" />
    </div>
  );
}

function SkeletonRow() {
  return (
    <tr className="border-b border-border">
      {Array.from({ length: 11 }).map((_, i) => (
        <td key={i} className="px-4 py-3">
          <div className="h-4 rounded bg-muted animate-pulse" />
        </td>
      ))}
    </tr>
  );
}

export default function Dashboard() {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [tradesReady, setTradesReady] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [sortKey, setSortKey] = useState<SortKey>("expiry_date");
  const [sortDir, setSortDir] = useState<SortDir>("asc");
  const [page, setPage] = useState(0);
  const [filterPreset, setFilterPreset] = useState<"all" | "today" | "last2" | "last3" | "last7" | "range">("all");
  const [rangeFrom, setRangeFrom] = useState<string>("");
  const [rangeTo, setRangeTo] = useState<string>("");
  const [syncing, setSyncing] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [tradesData, analysisData] = await Promise.all([fetchTrades(), fetchAnalysis()]);
      setTrades(tradesData);
      setTradesReady(analysisData.total_trades_analyzed ?? 0);
      setLastUpdate(new Date());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load trades");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    const onSettingsSaved = () => load();
    window.addEventListener("settings-saved", onSettingsSaved);
    return () => window.removeEventListener("settings-saved", onSettingsSaved);
  }, [load]);

  async function handleSyncFromSheet() {
    setSyncing(true);
    setError(null);
    try {
      const res = await syncSheetToDb();
      if (res.ok) {
        await load();
      } else {
        setError(res.error ?? "Sync failed");
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Sync failed");
    } finally {
      setSyncing(false);
    }
  }

  const filteredTrades = useMemo(() => {
    if (filterPreset === "all") return trades;

    const today = new Date();
    const todayIso = today.toISOString().slice(0, 10);

    function entryDateIso(t: Trade): string | null {
      if (!t.entry_time) return null;
      const d = new Date(t.entry_time);
      if (Number.isNaN(d.getTime())) return null;
      return d.toISOString().slice(0, 10);
    }

    if (filterPreset === "today") {
      return trades.filter((t) => entryDateIso(t) === todayIso);
    }

    const daysForPreset: Record<typeof filterPreset, number> = {
      all: 0,
      today: 0,
      last2: 2,
      last3: 3,
      last7: 7,
      range: 0,
    };

    if (filterPreset === "last2" || filterPreset === "last3" || filterPreset === "last7") {
      const days = daysForPreset[filterPreset];
      const cutoff = new Date();
      // Include today plus previous (days-1) days
      cutoff.setDate(today.getDate() - (days - 1));
      const cutoffIso = cutoff.toISOString().slice(0, 10);
      return trades.filter((t) => {
        const dIso = entryDateIso(t);
        return dIso !== null && dIso >= cutoffIso;
      });
    }

    // Custom range filter (rangeFrom / rangeTo are yyyy-mm-dd)
    if (filterPreset === "range") {
      if (!rangeFrom && !rangeTo) return trades;
      return trades.filter((t) => {
        const dIso = entryDateIso(t);
        if (dIso === null) return false;
        if (rangeFrom && dIso < rangeFrom) return false;
        if (rangeTo && dIso > rangeTo) return false;
        return true;
      });
    }

    return trades;
  }, [trades, filterPreset, rangeFrom, rangeTo]);

  const sortedTrades = useMemo(() => {
    const arr = [...filteredTrades];
    arr.sort((a, b) => {
      const aVal = a[sortKey];
      const bVal = b[sortKey];
      if (sortKey === "max_drawdown_percent" || sortKey === "current_price") {
        const aNum = aVal != null ? Number(aVal) : -1;
        const bNum = bVal != null ? Number(bVal) : -1;
        return sortDir === "asc" ? aNum - bNum : bNum - aNum;
      }
      if (typeof aVal === "string" && typeof bVal === "string") {
        return sortDir === "asc" ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
      }
      if (typeof aVal === "number" && typeof bVal === "number") {
        return sortDir === "asc" ? aVal - bVal : bVal - aVal;
      }
      return 0;
    });
    return arr;
  }, [filteredTrades, sortKey, sortDir]);

  const totalPages = Math.ceil(sortedTrades.length / PAGE_SIZE) || 1;
  const paginatedTrades = sortedTrades.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

  const handleSort = (key: SortKey) => {
    if (sortKey === key) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else {
      setSortKey(key);
      setSortDir("asc");
    }
  };

  const tradesTracked = trades.filter((t) => t.status?.toLowerCase() === "tracking" || t.status === "active").length || trades.length;

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-foreground">Dashboard</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Monitor tracked trades and performance
          </p>
        </div>
        <button
          type="button"
          onClick={handleSyncFromSheet}
          disabled={syncing || loading}
          className="inline-flex items-center gap-2 rounded-lg border border-border bg-card px-4 py-2 text-sm font-medium text-foreground shadow-sm hover:bg-muted/50 disabled:opacity-50"
        >
          {syncing ? (
            "Syncing…"
          ) : (
            <>
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden>
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Sync from Sheet
            </>
          )}
        </button>
      </div>
      {trades.length === 0 && !loading && (
        <div className="rounded-xl border border-amber-500/30 bg-amber-500/5 p-4 text-sm">
          <p className="font-medium text-amber-700 dark:text-amber-400">No trades yet</p>
          <p className="mt-1 text-muted-foreground">
            Click &quot;Sync from Sheet&quot; above to load trades from your Google Sheet. Or check{" "}
            <Link to="/sheet-reference" className="text-accent hover:underline">Sheet Reference</Link> to verify the sheet connection.
          </p>
        </div>
      )}

      {/* Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {loading ? (
          <>
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
          </>
        ) : (
          <>
            <div className="rounded-xl border border-border bg-card p-6 shadow-sm transition-colors">
              <p className="text-sm font-medium text-muted-foreground">Total Active Trades</p>
              <p className="mt-2 text-2xl font-semibold text-foreground">{trades.length}</p>
            </div>
            <div className="rounded-xl border border-border bg-card p-6 shadow-sm transition-colors">
              <p className="text-sm font-medium text-muted-foreground">Trades Being Tracked</p>
              <p className="mt-2 text-2xl font-semibold text-foreground">{tradesTracked}</p>
            </div>
            <div className="rounded-xl border border-border bg-card p-6 shadow-sm transition-colors">
              <p className="text-sm font-medium text-muted-foreground">Trades Ready for Analysis</p>
              <p className="mt-2 text-2xl font-semibold text-foreground">{tradesReady}</p>
            </div>
            <div className="rounded-xl border border-border bg-card p-6 shadow-sm transition-colors">
              <p className="text-sm font-medium text-muted-foreground">Last Update</p>
              <p className="mt-2 text-lg font-medium text-foreground">
                {lastUpdate ? lastUpdate.toLocaleTimeString() : "—"}
              </p>
            </div>
          </>
        )}
      </div>

      {/* Active Trades Table */}
      <div className="rounded-xl border border-border bg-card shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-border flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-lg font-semibold text-foreground">Active Trades</h2>
            <p className="text-sm text-muted-foreground mt-0.5">
              {loading
                ? "Loading…"
                : `${filteredTrades.length} trade${filteredTrades.length === 1 ? "" : "s"} shown`}
              {!loading && trades.length > 0 && (
                <>
                  {" "}
                  —{" "}
                  <span className="text-amber-600 dark:text-amber-400">
                    Rows highlighted in amber have no price data yet
                  </span>
                </>
              )}
            </p>
          </div>
          <div className="flex flex-col gap-2 sm:items-end">
            <button
              type="button"
              onClick={handleSyncFromSheet}
              disabled={syncing || loading}
              className="inline-flex items-center gap-2 rounded-lg border border-accent/50 bg-accent/10 px-3 py-1.5 text-sm font-medium text-accent hover:bg-accent/20 disabled:opacity-50"
            >
              {syncing ? (
                "Syncing…"
              ) : (
                <>
                  <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden>
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  Sync from Sheet
                </>
              )}
            </button>
            <div className="inline-flex rounded-lg border border-border bg-muted/40 p-0.5 text-xs sm:text-sm">
              <button
                type="button"
                onClick={() => {
                  setFilterPreset("all");
                  setPage(0);
                }}
                className={`px-3 py-1.5 rounded-md font-medium transition-colors ${
                  filterPreset === "all" ? "bg-card text-foreground shadow-sm" : "text-muted-foreground hover:text-foreground"
                }`}
              >
                All
              </button>
              <button
                type="button"
                onClick={() => {
                  setFilterPreset("today");
                  setPage(0);
                }}
                className={`px-3 py-1.5 rounded-md font-medium transition-colors ${
                  filterPreset === "today"
                    ? "bg-card text-foreground shadow-sm"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                Today
              </button>
              <button
                type="button"
                onClick={() => {
                  setFilterPreset("last2");
                  setPage(0);
                }}
                className={`px-3 py-1.5 rounded-md font-medium transition-colors ${
                  filterPreset === "last2"
                    ? "bg-card text-foreground shadow-sm"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                Last 2 days
              </button>
              <button
                type="button"
                onClick={() => {
                  setFilterPreset("last3");
                  setPage(0);
                }}
                className={`px-3 py-1.5 rounded-md font-medium transition-colors ${
                  filterPreset === "last3"
                    ? "bg-card text-foreground shadow-sm"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                Last 3 days
              </button>
              <button
                type="button"
                onClick={() => {
                  setFilterPreset("last7");
                  setPage(0);
                }}
                className={`px-3 py-1.5 rounded-md font-medium transition-colors ${
                  filterPreset === "last7"
                    ? "bg-card text-foreground shadow-sm"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                Last 7 days
              </button>
            </div>
            <div className="flex flex-wrap items-center gap-2 text-xs sm:text-sm">
              <span className="text-muted-foreground">Custom range:</span>
              <input
                type="date"
                value={rangeFrom}
                onChange={(e) => {
                  setRangeFrom(e.target.value);
                  setFilterPreset("range");
                  setPage(0);
                }}
                className="rounded-md border border-border bg-background px-2 py-1 text-xs sm:text-sm"
              />
              <span className="text-muted-foreground">to</span>
              <input
                type="date"
                value={rangeTo}
                onChange={(e) => {
                  setRangeTo(e.target.value);
                  setFilterPreset("range");
                  setPage(0);
                }}
                className="rounded-md border border-border bg-background px-2 py-1 text-xs sm:text-sm"
              />
              {(rangeFrom || rangeTo) && (
                <button
                  type="button"
                  onClick={() => {
                    setRangeFrom("");
                    setRangeTo("");
                    setFilterPreset("all");
                    setPage(0);
                  }}
                  className="text-xs text-accent hover:underline"
                >
                  Clear
                </button>
              )}
            </div>
          </div>
        </div>

        {error && (
          <div className="mx-6 mt-4 rounded-lg bg-danger/10 border border-danger/20 px-4 py-3 text-danger text-sm">
            {error}
          </div>
        )}

        <div className="overflow-x-auto">
          <table className="w-full min-w-[700px]">
            <thead>
              <tr className="border-b border-border bg-muted/30">
                {(
                  [
                    ["entry_time", "Date"],
                    ["ticker", "Ticker"],
                    ["strike_price", "Strike"],
                    ["option_type", "Type"],
                    ["expiry_date", "Expiry"],
                    ["entry_price", "Entry"],
                    ["current_price", "Current Price"],
                    ["drawdown_price", "Drawdown"],
                    ["max_drawdown_percent", "Drawdown %"],
                    ["analyst_name", "Analyst"],
                    ["status", "Status"],
                  ] as const
                ).map(([key, label]) => (
                  <th
                    key={key}
                    className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider cursor-pointer hover:text-foreground transition-colors"
                    onClick={() => handleSort(key)}
                  >
                    <span className="inline-flex items-center gap-1">
                      {label}
                      {sortKey === key && (
                        <span className="text-accent">{sortDir === "asc" ? "↑" : "↓"}</span>
                      )}
                    </span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {loading
                ? Array.from({ length: 5 }).map((_, i) => <SkeletonRow key={i} />)
                : paginatedTrades.map((t) => {
                    const hasDrawdownData = t.drawdown_price != null;
                    const dd = t.drawdown_price;
                    return (
                    <tr
                      key={t.id}
                      className={`border-b border-border hover:bg-muted/20 transition-colors ${
                        !hasDrawdownData
                          ? "bg-amber-500/5 dark:bg-amber-900/10 border-l-4 border-l-amber-500/50"
                          : ""
                      }`}
                    >
                      <td className="px-4 py-3 text-muted-foreground">
                        {t.entry_time ? new Date(t.entry_time).toLocaleDateString() : "—"}
                      </td>
                      <td className="px-4 py-3 font-medium">
                        <Link
                          to={`/trade/${t.id}`}
                          className="text-accent hover:underline"
                        >
                          {t.ticker}
                        </Link>
                      </td>
                      <td className="px-4 py-3 text-foreground">{t.strike_price}</td>
                      <td className="px-4 py-3">
                        <span
                          className={`inline-flex px-2 py-0.5 rounded text-xs font-medium ${
                            t.option_type === "CALL"
                              ? "bg-success/15 text-success"
                              : "bg-danger/15 text-danger"
                          }`}
                        >
                          {t.option_type}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-muted-foreground">{t.expiry_date}</td>
                      <td className="px-4 py-3 text-foreground">${t.entry_price.toFixed(2)}</td>
                      <td className="px-4 py-3" title={t.current_price_source === "last" ? "Last price (not live) — compare with your broker" : "Live price — compare with your broker"}>
                        {t.current_price != null ? (
                          t.current_price_source === "live" ? (
                            <span className="font-medium text-foreground">${t.current_price.toFixed(2)}</span>
                          ) : (
                            <span className="font-medium text-muted-foreground">Last: ${t.current_price.toFixed(2)}</span>
                          )
                        ) : (
                          <span className="text-amber-600 dark:text-amber-400 text-xs font-medium">—</span>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        {hasDrawdownData ? (
                          <span className="font-medium text-danger">
                            ${dd!.toFixed(2)}
                          </span>
                        ) : (
                          <span className="text-amber-600 dark:text-amber-400 text-xs font-medium" title="No price data yet — tracker may have API issues or market closed">
                            No data
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        {t.max_drawdown_percent != null ? (
                          <span className={t.max_drawdown_percent > 0 ? "font-medium text-danger" : "text-muted-foreground"}>
                            {t.max_drawdown_percent.toFixed(1)}%
                          </span>
                        ) : (
                          <span className="text-amber-600 dark:text-amber-400 text-xs font-medium">
                            No data
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-muted-foreground">{t.analyst_name || "—"}</td>
                      <td className="px-4 py-3">
                        <span className="text-sm text-muted-foreground capitalize">
                          {t.status || "—"}
                        </span>
                      </td>
                    </tr>
                  );
                  })}
            </tbody>
          </table>
        </div>

        {!loading && totalPages > 1 && (
          <div className="flex items-center justify-between px-6 py-3 border-t border-border">
            <p className="text-sm text-muted-foreground">
              Page {page + 1} of {totalPages}
            </p>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                disabled={page === 0}
                className="rounded-md px-3 py-1.5 text-sm font-medium bg-muted text-muted-foreground hover:bg-muted/80 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Previous
              </button>
              <button
                type="button"
                onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                disabled={page >= totalPages - 1}
                className="rounded-md px-3 py-1.5 text-sm font-medium bg-muted text-muted-foreground hover:bg-muted/80 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
