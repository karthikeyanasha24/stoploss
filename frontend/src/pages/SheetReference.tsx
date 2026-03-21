import { useEffect, useState } from "react";
import { fetchSheetReference } from "../lib/api";
import type { SheetReference as SheetReferenceType, SheetTradeVerbose } from "../lib/api";

const STATUS_BADGES: Record<SheetTradeVerbose["status"], string> = {
  on_dashboard: "bg-success/15 text-success",
  expired: "bg-muted text-muted-foreground",
  no_expiry: "bg-amber-500/15 text-amber-600 dark:text-amber-400",
  parse_failed: "bg-danger/15 text-danger",
  invalid_entry: "bg-danger/15 text-danger",
  futures: "bg-sky-500/15 text-sky-600 dark:text-sky-400",
};

function formatTakeProfitTargets(t: SheetTradeVerbose) {
  const targets =
    t.take_profit_targets_order?.length ? t.take_profit_targets_order : t.take_profit_targets;
  if (!targets?.length) {
    return "—";
  }
  return targets.map((target, i) => `TP${i + 1}: $${target.toFixed(2)}`).join(" · ");
}

function SkeletonCard() {
  return (
    <div className="rounded-xl border border-border bg-card p-8 animate-pulse">
      <div className="h-4 w-40 rounded bg-muted mb-4" />
      <div className="h-12 w-24 rounded bg-muted" />
    </div>
  );
}

export default function SheetReference() {
  const [data, setData] = useState<SheetReferenceType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const result = await fetchSheetReference();
        if (!cancelled) setData(result);
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : "Failed to load sheet reference");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
  }, []);

  if (loading || !data) {
    return (
      <div className="space-y-8">
        <div>
          <h1 className="text-2xl font-semibold text-foreground">Sheet Reference</h1>
          <p className="mt-1 text-sm text-muted-foreground">All trades from Google Sheet with status</p>
        </div>
        {error && (
          <div className="rounded-lg bg-danger/10 border border-danger/20 px-4 py-3 text-danger">
            {error}
          </div>
        )}
        <SkeletonCard />
      </div>
    );
  }

  return (
    <div className="space-y-6 sm:space-y-8">
      <div>
        <h1 className="text-2xl font-semibold text-foreground">Sheet Reference</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          All trades from your Google Sheet — why each is or isn&apos;t on the dashboard
        </p>
      </div>

      {error && (
        <div className="rounded-lg bg-danger/10 border border-danger/20 px-4 py-3 text-danger">
          {error}
        </div>
      )}
      {data.error && (
        <div className="rounded-lg bg-danger/10 border border-danger/20 px-4 py-3 text-danger">
          {data.error}
        </div>
      )}

      {!data.error && (
        <div className="rounded-xl border border-border bg-muted/20 p-4 text-sm text-muted-foreground">
          <p className="font-medium text-foreground mb-2">Status legend:</p>
          <ul className="space-y-1">
            <li><span className="inline-flex px-2 py-0.5 rounded text-xs font-medium bg-success/15 text-success">on_dashboard</span> — Active trade, tracked on Dashboard</li>
            <li><span className="inline-flex px-2 py-0.5 rounded text-xs font-medium bg-muted text-muted-foreground">expired</span> — Option expired, not shown on Dashboard</li>
            <li><span className="inline-flex px-2 py-0.5 rounded text-xs font-medium bg-amber-500/15 text-amber-600">no_expiry</span> — Add Exp:MM/DD/YYYY to Ticker/Strike to track</li>
            <li><span className="inline-flex px-2 py-0.5 rounded text-xs font-medium bg-sky-500/15 text-sky-600">futures</span> — Futures/index level; only options are tracked</li>
            <li><span className="inline-flex px-2 py-0.5 rounded text-xs font-medium bg-danger/15 text-danger">parse_failed</span> — Ticker format not recognized</li>
            <li><span className="inline-flex px-2 py-0.5 rounded text-xs font-medium bg-danger/15 text-danger">invalid_entry</span> — Missing or invalid Entry price</li>
          </ul>
        </div>
      )}

      <div className="space-y-6">
        {data.sheets.map((sheet) => (
          <div key={sheet.name} className="overflow-hidden rounded-xl border border-border bg-card shadow-sm">
            <div className="border-b border-border bg-muted/30 px-4 py-4 sm:px-6">
              <h2 className="text-lg font-semibold text-foreground">{sheet.name}</h2>
              {sheet.skip_reason && (
                <p className="text-sm text-muted-foreground mt-1">{sheet.skip_reason}</p>
              )}
              {sheet.error && (
                <p className="text-sm text-danger mt-1">{sheet.error}</p>
              )}
              {!sheet.skip_reason && !sheet.error && (
                <p className="text-sm text-muted-foreground mt-1">
                  {sheet.trades.length} trade{sheet.trades.length === 1 ? "" : "s"}
                  {sheet.trades.filter((t) => t.status === "on_dashboard").length > 0 && (
                    <> — {sheet.trades.filter((t) => t.status === "on_dashboard").length} on Dashboard</>
                  )}
                </p>
              )}
            </div>
            {sheet.trades.length > 0 && (
              <>
              <div className="space-y-3 p-4 sm:hidden">
                {sheet.trades.map((t, i) => (
                  <div key={i} className="rounded-xl border border-border bg-background/40 p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="text-sm font-semibold text-foreground break-words">{t.ticker_raw}</p>
                        <p className="mt-1 text-sm text-muted-foreground">
                          Entry: {t.entry_price != null ? `$${t.entry_price.toFixed(2)}` : "—"}
                        </p>
                      </div>
                      <span
                        className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${
                          STATUS_BADGES[t.status]
                        }`}
                      >
                        {t.status}
                      </span>
                    </div>
                    <div className="mt-3 grid grid-cols-1 gap-3 text-sm">
                      <div className="rounded-lg bg-muted/30 p-3">
                        <p className="text-xs uppercase tracking-wide text-muted-foreground">Take profits</p>
                        <p className="mt-1 text-foreground">{formatTakeProfitTargets(t)}</p>
                      </div>
                      <div className="rounded-lg bg-muted/30 p-3">
                        <p className="text-xs uppercase tracking-wide text-muted-foreground">Expiry</p>
                        <p className="mt-1 text-foreground">{t.expiry_date ?? "—"}</p>
                      </div>
                      <div className="rounded-lg bg-muted/30 p-3">
                        <p className="text-xs uppercase tracking-wide text-muted-foreground">Reason</p>
                        <p className="mt-1 text-muted-foreground">{t.reason}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="hidden overflow-x-auto sm:block">
                <table className="w-full min-w-[700px]">
                  <thead>
                    <tr className="border-b border-border bg-muted/20">
                      <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                        Ticker/Strike
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                        Entry
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                        Take Profits
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                        Expiry
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                        Reason
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {sheet.trades.map((t, i) => (
                      <tr
                        key={i}
                        className="border-b border-border hover:bg-muted/20 transition-colors"
                      >
                        <td className="px-4 py-3 font-medium text-foreground">
                          {t.ticker_raw}
                        </td>
                        <td className="px-4 py-3 text-muted-foreground">
                          {t.entry_price != null ? `$${t.entry_price.toFixed(2)}` : "—"}
                        </td>
                        <td className="px-4 py-3 text-muted-foreground">
                          {formatTakeProfitTargets(t)}
                        </td>
                        <td className="px-4 py-3 text-muted-foreground">
                          {t.expiry_date ?? "—"}
                        </td>
                        <td className="px-4 py-3">
                          <span
                            className={`inline-flex px-2 py-0.5 rounded text-xs font-medium ${
                              STATUS_BADGES[t.status]
                            }`}
                          >
                            {t.status}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-sm text-muted-foreground max-w-md">
                          {t.reason}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
