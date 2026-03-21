import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchAnalysis } from "../lib/api";
import type { Analysis as AnalysisType } from "../lib/api";

function SkeletonCard() {
  return (
    <div className="rounded-xl border border-border bg-card p-8 animate-pulse">
      <div className="h-4 w-40 rounded bg-muted mb-4" />
      <div className="h-12 w-24 rounded bg-muted" />
    </div>
  );
}

export default function Analysis() {
  const [data, setData] = useState<AnalysisType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const result = await fetchAnalysis();
        if (!cancelled) setData(result);
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : "Failed to load analysis");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    const onSettingsSaved = () => {
      if (!cancelled) load();
    };
    window.addEventListener("settings-saved", onSettingsSaved);
    return () => {
      cancelled = true;
      window.removeEventListener("settings-saved", onSettingsSaved);
    };
  }, []);

  const maxHitRate = data?.stop_results?.length
    ? Math.max(...data.stop_results.map((r) => r.trades_stopped_out_pct))
    : 100;

  return (
    <div className="space-y-6 sm:space-y-8">
      <div>
        <h1 className="text-2xl font-semibold text-foreground">Stop-Loss Analysis</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Recommended stop levels based on drawdown from alert until the first take-profit hit
        </p>
      </div>

      {error && (
        <div className="rounded-lg bg-danger/10 border border-danger/20 px-4 py-3 text-danger">
          {error}
        </div>
      )}

      {/* Recommended Stop Hero */}
      <div className="overflow-hidden rounded-xl border border-accent/40 bg-card shadow-lg bg-gradient-to-br from-accent/5 to-transparent">
        <div className="p-5 sm:p-8 md:p-10">
          {loading ? (
            <SkeletonCard />
          ) : data?.recommended_stop != null ? (
            <div>
              <p className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
                Recommended Stop
              </p>
              <p className="mt-3 text-3xl font-bold text-accent sm:text-4xl md:text-5xl">
                {data.recommended_stop}%
              </p>
              {data.summary && (
                <p className="mt-3 text-muted-foreground max-w-xl">{data.summary}</p>
              )}
              {data.total_trades_analyzed != null && (
                <p className="mt-2 text-sm text-muted-foreground">
                  Based on {data.total_trades_analyzed} trade{data.total_trades_analyzed === 1 ? "" : "s"} that hit a take-profit target after ≥{data.analysis_days ?? 7} days of tracking
                </p>
              )}
              {(data.skipped_without_take_profit || data.skipped_without_take_profit_hit) ? (
                <p className="mt-2 text-sm text-muted-foreground">
                  Skipped {data.skipped_without_take_profit ?? 0} trade{data.skipped_without_take_profit === 1 ? "" : "s"} with no take-profit target and {data.skipped_without_take_profit_hit ?? 0} trade{data.skipped_without_take_profit_hit === 1 ? "" : "s"} that have not hit their first take-profit yet.
                </p>
              ) : null}
            </div>
          ) : (
            <div>
              <p className="text-muted-foreground">
                {data?.message ?? "No analysis available yet."}
              </p>
              <Link to="/" className="mt-4 inline-block text-accent hover:underline">
                View Dashboard →
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Stop Performance Table */}
      <div className="rounded-xl border border-border bg-card shadow-sm overflow-hidden">
        <div className="border-b border-border px-4 py-4 sm:px-6">
          <h2 className="text-lg font-semibold text-foreground">Stop Performance</h2>
          <p className="text-sm text-muted-foreground mt-0.5">
            Hit rate and survival rate by stop level
          </p>
        </div>
        <div className="sm:hidden">
          {loading ? (
            <div className="space-y-4 p-4">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="h-28 animate-pulse rounded-xl bg-muted" />
              ))}
            </div>
          ) : data?.stop_results?.length ? (
            <div className="space-y-3 p-4">
              {data.stop_results.map((r) => {
                const survived = 100 - r.trades_stopped_out_pct;
                return (
                  <div key={r.stop_percent} className="rounded-xl border border-border bg-background/40 p-4">
                    <div className="flex items-center justify-between gap-3">
                      <h3 className="text-base font-semibold text-foreground">{r.stop_percent}% stop</h3>
                      <span className="text-sm text-muted-foreground">
                        {r.trades_stopped} / {r.total_trades} trades
                      </span>
                    </div>
                    <div className="mt-4 space-y-3">
                      <div>
                        <div className="mb-1 flex items-center justify-between text-sm">
                          <span className="text-muted-foreground">Hit rate</span>
                          <span className="font-medium text-danger">{r.trades_stopped_out_pct.toFixed(1)}%</span>
                        </div>
                        <div className="h-2 rounded-full bg-muted">
                          <div
                            className="h-full rounded-full bg-danger/80"
                            style={{ width: `${r.trades_stopped_out_pct}%` }}
                          />
                        </div>
                      </div>
                      <div>
                        <div className="mb-1 flex items-center justify-between text-sm">
                          <span className="text-muted-foreground">Survived</span>
                          <span className="font-medium text-success">{survived.toFixed(1)}%</span>
                        </div>
                        <div className="h-2 rounded-full bg-muted">
                          <div
                            className="h-full rounded-full bg-success/80"
                            style={{ width: `${survived}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="p-4 text-muted-foreground">No stop results available.</div>
          )}
        </div>

        <div className="hidden overflow-x-auto sm:block">
          {loading ? (
            <div className="p-6 space-y-4">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="h-12 rounded bg-muted animate-pulse" />
              ))}
            </div>
          ) : data?.stop_results?.length ? (
            <>
              <table className="w-full min-w-[500px]">
                <thead>
                  <tr className="border-b border-border bg-muted/30">
                    <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                      Stop %
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                      Hit Rate %
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                      Survived %
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                      Trades
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {data.stop_results.map((r) => {
                    const survived = 100 - r.trades_stopped_out_pct;
                    return (
                      <tr key={r.stop_percent} className="border-b border-border hover:bg-muted/20 transition-colors">
                        <td className="px-6 py-4 font-medium text-foreground">{r.stop_percent}%</td>
                        <td className="px-6 py-4">
                          <span className="text-danger font-medium">{r.trades_stopped_out_pct.toFixed(1)}%</span>
                        </td>
                        <td className="px-6 py-4">
                          <span className="text-success font-medium">{survived.toFixed(1)}%</span>
                        </td>
                        <td className="px-6 py-4 text-muted-foreground">
                          {r.trades_stopped} / {r.total_trades}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>

              {/* Optional Bar Chart */}
              <div className="p-6 border-t border-border">
                <h3 className="text-sm font-medium text-muted-foreground mb-4">Stop % vs Hit Rate</h3>
                <div className="space-y-3">
                  {data.stop_results.map((r) => (
                    <div key={r.stop_percent} className="flex items-center gap-3">
                      <span className="w-12 text-sm font-medium text-foreground">{r.stop_percent}%</span>
                      <div className="flex-1 h-6 rounded-md bg-muted overflow-hidden">
                        <div
                          className="h-full rounded-md bg-danger/80 transition-all duration-500"
                          style={{ width: `${(r.trades_stopped_out_pct / (maxHitRate || 1)) * 100}%` }}
                        />
                      </div>
                      <span className="w-14 text-right text-sm text-muted-foreground">
                        {r.trades_stopped_out_pct.toFixed(1)}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </>
          ) : (
            <div className="p-6 text-muted-foreground">
              No stop results available.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
