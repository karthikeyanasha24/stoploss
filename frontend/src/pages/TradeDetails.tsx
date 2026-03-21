import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { fetchStats, fetchTrades } from "../lib/api";
import type { TradeStats, Trade } from "../lib/api";

function formatCurrency(value: number | null | undefined) {
  return value != null ? `$${value.toFixed(2)}` : "—";
}

function formatTakeProfitTargets(targets: number[] | undefined, order?: number[] | undefined) {
  const list = order?.length ? order : targets;
  if (!list?.length) {
    return "No TP levels ";
  }
  return list.map((target, i) => `TP${i + 1}: $${target.toFixed(2)}`).join(" · ");
}

function SkeletonCard() {
  return (
    <div className="rounded-xl border border-border bg-card p-6 animate-pulse">
      <div className="h-4 w-20 rounded bg-muted mb-4" />
      <div className="h-8 w-32 rounded bg-muted mb-2" />
      <div className="h-4 w-24 rounded bg-muted" />
    </div>
  );
}

export default function TradeDetails() {
  const { id } = useParams<{ id: string }>();
  const [data, setData] = useState<TradeStats | null>(null);
  const [trade, setTrade] = useState<Trade | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    const tradeId = parseInt(id, 10);
    if (Number.isNaN(tradeId)) {
      setError("Invalid trade ID");
      setLoading(false);
      return;
    }

    let cancelled = false;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const [statsResult, tradesList] = await Promise.all([fetchStats(tradeId), fetchTrades()]);
        const found = tradesList.find((t) => t.id === tradeId);
        if (!cancelled) {
          setData(statsResult);
          setTrade(found ?? null);
        }
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : "Failed to load trade");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, [id]);

  if (!id) {
    return (
      <div className="space-y-6">
        <p className="text-muted-foreground">No trade ID provided.</p>
        <Link to="/" className="text-accent hover:underline">Back to Dashboard</Link>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="rounded-lg bg-danger/10 border border-danger/20 px-4 py-3 text-danger">
          {error}
        </div>
        <Link to="/" className="text-accent hover:underline">Back to Dashboard</Link>
      </div>
    );
  }

  const stats = data?.stats;

  return (
    <div className="space-y-6 sm:space-y-8">
      <div className="flex items-start gap-3 sm:items-center sm:gap-4">
        <Link
          to="/"
          className="rounded-md p-2 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
          aria-label="Back to Dashboard"
        >
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </Link>
        <div className="min-w-0">
          <h1 className="text-2xl font-semibold text-foreground">Trade Details</h1>
          <p className="text-sm text-muted-foreground">Price movement and stats</p>
        </div>
      </div>

      {/* Trade Summary */}
      <div className="overflow-hidden rounded-xl border border-border bg-card shadow-sm">
        <div className="border-b border-border px-4 py-4 sm:px-6">
          <h2 className="text-lg font-semibold text-foreground">Trade Summary</h2>
        </div>
        {loading ? (
          <div className="p-4 sm:p-6">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4">
              {Array.from({ length: 6 }).map((_, i) => (
                <SkeletonCard key={i} />
              ))}
            </div>
          </div>
        ) : data || trade ? (
          <div className="p-4 sm:p-6">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Ticker</p>
                <p className="mt-1 text-lg font-semibold text-foreground">{data?.ticker ?? trade?.ticker ?? "—"}</p>
              </div>
              {trade && (
                <>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Strike</p>
                    <p className="mt-1 text-lg font-semibold text-foreground">{trade.strike_price}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Type</p>
                    <p className="mt-1">
                      <span className={`inline-flex px-2 py-0.5 rounded text-sm font-medium ${
                        trade.option_type === "CALL" ? "bg-success/15 text-success" : "bg-danger/15 text-danger"
                      }`}>
                        {trade.option_type}
                      </span>
                    </p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Expiry</p>
                    <p className="mt-1 text-lg font-semibold text-foreground">{trade.expiry_date}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Analyst</p>
                    <p className="mt-1 text-lg font-semibold text-foreground">{trade.analyst_name || "—"}</p>
                  </div>
                </>
              )}
              <div>
                <p className="text-sm font-medium text-muted-foreground">Entry Price</p>
                <p className="mt-1 text-lg font-semibold text-foreground">${(data?.entry_price ?? trade?.entry_price ?? 0).toFixed(2)}</p>
              </div>
            </div>
          </div>
        ) : null}
      </div>

      {/* Stats Panel */}
      <div className="overflow-hidden rounded-xl border border-border bg-card shadow-sm">
        <div className="border-b border-border px-4 py-4 sm:px-6">
          <h2 className="text-lg font-semibold text-foreground">Price Movement Stats</h2>
          <p className="text-sm text-muted-foreground mt-0.5">
            Overall price stats plus drawdown from alert until the first take-profit hit
          </p>
        </div>
        <div className="p-4 sm:p-6">
          {loading ? (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
            </div>
          ) : stats ? (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
              <div className="rounded-lg border border-border bg-muted/20 p-6">
                <p className="text-sm font-medium text-muted-foreground">Lowest Price</p>
                <p className="mt-2 text-2xl font-semibold text-foreground">
                  ${stats.lowest_price.toFixed(2)}
                </p>
              </div>
              <div className="rounded-lg border border-border bg-muted/20 p-6">
                <p className="text-sm font-medium text-muted-foreground">Highest Price</p>
                <p className="mt-2 text-2xl font-semibold text-foreground">
                  ${stats.highest_price.toFixed(2)}
                </p>
              </div>
              <div className="rounded-lg border border-border bg-muted/20 p-6">
                <p className="text-sm font-medium text-muted-foreground">Max Drawdown Since Entry</p>
                <p className={`mt-2 text-2xl font-semibold ${stats.max_drawdown_percent >= 0 ? "text-danger" : "text-success"}`}>
                  {stats.max_drawdown_percent >= 0
                    ? `${stats.max_drawdown_percent.toFixed(1)}%`
                    : `${stats.max_drawdown_percent.toFixed(1)}%`}
                </p>
              </div>
              <div className="rounded-lg border border-border bg-muted/20 p-6">
                <p className="text-sm font-medium text-muted-foreground">Drawdown Before 1st TP</p>
                <p className="mt-2 text-2xl font-semibold text-danger">
                  {stats.drawdown_before_take_profit_percent != null
                    ? `${stats.drawdown_before_take_profit_percent.toFixed(1)}%`
                    : "Pending"}
                </p>
                <p className="mt-2 text-sm text-muted-foreground">
                  Lowest before TP: {formatCurrency(stats.drawdown_before_take_profit_price)}
                </p>
              </div>
            </div>
          ) : (
            <p className="text-muted-foreground">No price stats available yet. Trade may need more tracking time.</p>
          )}
        </div>
      </div>

      <div className="overflow-hidden rounded-xl border border-border bg-card shadow-sm">
        <div className="border-b border-border px-4 py-4 sm:px-6">
          <h2 className="text-lg font-semibold text-foreground">Take-Profit Tracking</h2>
        </div>
        <div className="grid grid-cols-1 gap-4 p-4 sm:grid-cols-2 sm:p-6 xl:grid-cols-3">
          <div className="rounded-lg border border-border bg-muted/20 p-6">
            <p className="text-sm font-medium text-muted-foreground">Targets From Sheet</p>
            <p className="mt-2 text-lg font-semibold text-foreground">
              {formatTakeProfitTargets(
                data?.take_profit_targets ?? trade?.take_profit_targets,
                data?.take_profit_targets_order ?? trade?.take_profit_targets_order,
              )}
            </p>
          </div>
          <div className="rounded-lg border border-border bg-muted/20 p-6">
            <p className="text-sm font-medium text-muted-foreground">First TP Used For Analysis</p>
            <p className="mt-2 text-lg font-semibold text-foreground">
              {formatCurrency(stats?.take_profit_target_price)}
            </p>
            <p className="mt-2 text-sm text-muted-foreground">
              First profitable target above the alert price.
            </p>
          </div>
          <div className="rounded-lg border border-border bg-muted/20 p-6">
            <p className="text-sm font-medium text-muted-foreground">First TP Hit</p>
            <p className="mt-2 text-lg font-semibold text-foreground">
              {formatCurrency(stats?.take_profit_hit_price)}
            </p>
            <p className="mt-2 text-sm text-muted-foreground">
              {stats?.take_profit_hit_at ? new Date(stats.take_profit_hit_at).toLocaleString() : "Not hit yet"}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
