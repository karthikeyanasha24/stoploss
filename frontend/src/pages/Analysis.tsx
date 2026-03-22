import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchAnalysis } from "../lib/api";
import type { Analysis as AnalysisType } from "../lib/api";
import { downloadAnalysisExcel } from "../lib/exportExcel";

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

  function handleExportAnalysis() {
    if (!data) return;
    downloadAnalysisExcel(data);
  }

  return (
    <div className="space-y-6 sm:space-y-8">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-foreground">Stop-Loss Analysis</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Drawdown on the path to TP1: (min price before TP1 − entry) / entry (negative % = underwater). TP1 is the first exit above entry in sheet order. Add column &quot;Lowest Price Before TP1&quot; for historical trades without full price logs.
          </p>
        </div>
        <button
          type="button"
          onClick={handleExportAnalysis}
          disabled={loading || !data}
          className="inline-flex w-full sm:w-auto shrink-0 items-center justify-center gap-2 rounded-lg border border-border bg-card px-4 py-2 text-sm font-medium text-foreground shadow-sm hover:bg-muted/50 disabled:opacity-50"
          title="Downloads an Excel workbook: Summary, Stop levels, and Trades in sample (full tables — no scrolling)."
        >
          <svg className="h-4 w-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden>
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Export to Excel
        </button>
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
              {(data.excluded_lotto_outliers ?? 0) > 0 && (
                <p className="mt-2 text-sm text-muted-foreground">
                  Stop simulation uses {data.total_trades_for_stop_simulation ?? 0} trade
                  {(data.total_trades_for_stop_simulation ?? 0) === 1 ? "" : "s"} (excluded{" "}
                  {data.excluded_lotto_outliers} with signed drawdown ≤{" "}
                  {data.excluded_signed_drawdown_threshold_percent ?? -70}% as lotto/outliers).
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

      {!loading && data?.drawdown_signed_summary && (
        <div className="rounded-xl border border-border bg-muted/20 px-4 py-3 sm:px-6 text-sm text-muted-foreground">
          <p className="font-medium text-foreground">Signed drawdown (before TP1)</p>
          <p className="mt-1">
            All trades — Avg: {data.drawdown_signed_summary.average_percent ?? "—"}% · Min:{" "}
            {data.drawdown_signed_summary.min_percent ?? "—"}% · Max:{" "}
            {data.drawdown_signed_summary.max_percent ?? "—"}%
          </p>
          {(data.drawdown_signed_summary.average_percent_excluding_outliers != null ||
            data.drawdown_signed_summary.min_percent_excluding_outliers != null) && (
            <p className="mt-1">
              Excluding signed ≤ {data.excluded_signed_drawdown_threshold_percent ?? -70}% — Avg:{" "}
              {data.drawdown_signed_summary.average_percent_excluding_outliers ?? "—"}% · Min:{" "}
              {data.drawdown_signed_summary.min_percent_excluding_outliers ?? "—"}% · Max:{" "}
              {data.drawdown_signed_summary.max_percent_excluding_outliers ?? "—"}%
            </p>
          )}
          {data.drawdown_signed_summary.note && (
            <p className="mt-1 text-xs opacity-90">{data.drawdown_signed_summary.note}</p>
          )}
          {data.drawdown_signed_summary.outlier_note && (
            <p className="mt-1 text-xs opacity-90">{data.drawdown_signed_summary.outlier_note}</p>
          )}
        </div>
      )}

      {!loading && data?.trades_detail && data.trades_detail.length > 0 && (
        <div className="rounded-xl border border-border bg-card shadow-sm overflow-hidden">
          <div className="border-b border-border px-4 py-4 sm:px-6">
            <h2 className="text-lg font-semibold text-foreground">Trades in this sample</h2>
            <p className="text-sm text-muted-foreground mt-0.5">
              Entry, min before TP1, signed drawdown %, TP1 % (upside to first target)
            </p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[640px] text-sm">
              <thead>
                <tr className="border-b border-border bg-muted/30">
                  <th className="px-4 py-2 text-left text-xs font-medium text-muted-foreground uppercase">Ticker</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-muted-foreground uppercase">Entry</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-muted-foreground uppercase">Min before TP1</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-muted-foreground uppercase">DD % (signed)</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-muted-foreground uppercase">TP1 %</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-muted-foreground uppercase">Source</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-muted-foreground uppercase">Stop sim</th>
                </tr>
              </thead>
              <tbody>
                {data.trades_detail.map((row, idx) => (
                  <tr
                    key={idx}
                    className={`border-b border-border hover:bg-muted/15 ${row.excluded_from_stop_analysis ? "opacity-75" : ""}`}
                  >
                    <td className="px-4 py-2 font-medium text-foreground">{row.ticker}</td>
                    <td className="px-4 py-2 text-muted-foreground">${row.entry_price.toFixed(2)}</td>
                    <td className="px-4 py-2 text-muted-foreground">
                      {row.min_price_before_tp1 != null ? `$${row.min_price_before_tp1.toFixed(2)}` : "—"}
                    </td>
                    <td className="px-4 py-2 text-muted-foreground">
                      {row.drawdown_percent_signed != null ? `${row.drawdown_percent_signed}%` : "—"}
                    </td>
                    <td className="px-4 py-2 text-muted-foreground">
                      {row.tp1_upside_percent != null ? `${row.tp1_upside_percent.toFixed(1)}%` : "—"}
                    </td>
                    <td className="px-4 py-2 text-muted-foreground text-xs">{row.min_before_tp1_source ?? "—"}</td>
                    <td className="px-4 py-2 text-muted-foreground text-xs">
                      {row.excluded_from_stop_analysis ? "Excluded (outlier)" : "Included"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

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
