import type { ReactNode } from "react";
import { Link } from "react-router-dom";

function Section({
  title,
  id,
  children,
}: {
  title: string;
  id: string;
  children: ReactNode;
}) {
  return (
    <section id={id} className="scroll-mt-24 rounded-xl border border-border bg-card p-5 sm:p-6 shadow-sm">
      <h2 className="text-lg font-semibold text-foreground">{title}</h2>
      <div className="mt-3 space-y-3 text-sm text-muted-foreground leading-relaxed">{children}</div>
    </section>
  );
}

export default function ClientGuide() {
  return (
    <div className="space-y-8 sm:space-y-10 max-w-3xl">
      <div>
        <h1 className="text-2xl font-semibold text-foreground">How this app works</h1>
        <p className="mt-2 text-sm text-muted-foreground leading-relaxed">
          Plain-language notes for each area of Stop-Loss — what the numbers mean, how they are calculated, and how
          the pages fit together.
        </p>
      </div>

      <section
        id="simple"
        className="scroll-mt-24 rounded-xl border border-accent/30 bg-accent/5 p-5 sm:p-6 shadow-sm"
      >
        <h2 className="text-lg font-semibold text-foreground">Start here (no trading or tech background needed)</h2>
        <div className="mt-3 space-y-3 text-sm text-muted-foreground leading-relaxed">
          <p>
            <strong className="text-foreground">What problem does this solve?</strong> You run trades from a spreadsheet.
            This app copies those trades in, pulls <strong className="text-foreground">real option prices</strong> on a
            schedule, and remembers the <strong className="text-foreground">worst price</strong> each trade hit along the
            way. That helps answer: &quot;How much pain happened before I got to my profit goal?&quot; — without you
            hand-calculating every line.
          </p>
          <p>
            <strong className="text-foreground">Words on the screen (very short):</strong>{" "}
            <em>Entry</em> = what you paid (premium). <em>Current price</em> = what the option is worth last time we
            checked. <em>Take profit (TP1, TP2…)</em> = prices where you plan to take money off the table.{" "}
            <em>Drawdown (DD)</em> = how far price fell against you, as a percent of entry. Big red numbers mean the
            position went deeply underwater at some point before (or until) you hit a target.
          </p>
          <p>
            <strong className="text-foreground">Two different &quot;drawdown&quot; ideas:</strong>{" "}
            <strong className="text-foreground">Current DD %</strong> uses the lowest price seen since we started
            tracking (even after a profit target is hit). <strong className="text-foreground">Babji DD %</strong> only
            looks at the path <em>until the first time</em> price reaches your first target (TP1), then stops — so it
            matches the question &quot;what stop would have fired before I got to TP1?&quot;
          </p>
          <p>
            <strong className="text-foreground">Analysis page:</strong> uses past trades that actually reached TP1 and
            tests hypothetical stops (15%–40% of entry). It recommends a stop level that would not have cut too many of
            those winners before TP1 — see that page for <em>your</em> numbers. It is a statistic from history, not a
            guarantee of the future.
          </p>
          <p>
            <strong className="text-foreground">Dashboard tip:</strong> use <strong className="text-foreground">Print / Save PDF</strong>{" "}
            (top of Dashboard) to save a snapshot without dragging scrollbars; in the print dialog, choose{" "}
            <strong className="text-foreground">Landscape</strong> if the table is still wide on your screen.
          </p>
        </div>
      </section>

      <nav
        aria-label="On this page"
        className="rounded-xl border border-border bg-muted/20 px-4 py-3 text-sm"
      >
        <p className="font-medium text-foreground mb-2">On this page</p>
        <ul className="grid gap-1.5 sm:grid-cols-2 text-accent">
          <li>
            <a href="#simple" className="hover:underline">
              Start here (simplest)
            </a>
          </li>
          <li>
            <a href="#overview" className="hover:underline">
              Big picture
            </a>
          </li>
          <li>
            <a href="#dashboard" className="hover:underline">
              Dashboard
            </a>
          </li>
          <li>
            <a href="#tp1" className="hover:underline">
              TP1 &amp; take profits
            </a>
          </li>
          <li>
            <a href="#drawdowns" className="hover:underline">
              Current DD % vs Babji DD %
            </a>
          </li>
          <li>
            <a href="#sources" className="hover:underline">
              Live, Frozen, Limited, N/A
            </a>
          </li>
          <li>
            <a href="#analysis" className="hover:underline">
              Analysis &amp; recommended stop
            </a>
          </li>
          <li>
            <a href="#sheet-ref" className="hover:underline">
              Sheet Reference
            </a>
          </li>
          <li>
            <a href="#logs" className="hover:underline">
              Logs
            </a>
          </li>
          <li>
            <a href="#disclaimer" className="hover:underline">
              Important caveat
            </a>
          </li>
        </ul>
      </nav>

      <Section id="overview" title="Big picture">
        <p>
          Stop-Loss connects to your trade sheet, keeps a list of <strong className="text-foreground">active</strong>{" "}
          option trades, and periodically records option prices. From that history it computes{" "}
          <strong className="text-foreground">drawdown</strong> (how far price moved against you) and, when you define
          take-profit levels, <strong className="text-foreground">drawdown before TP1</strong> — the worst adverse move
          on the way to your first profit target.
        </p>
        <p>
          Use the sidebar to open the{" "}
          <Link to="/" className="text-accent font-medium hover:underline">
            Dashboard
          </Link>
          ,{" "}
          <Link to="/analysis" className="text-accent font-medium hover:underline">
            Analysis
          </Link>
          ,{" "}
          <Link to="/sheet-reference" className="text-accent font-medium hover:underline">
            Sheet Reference
          </Link>
          , and{" "}
          <Link to="/logs" className="text-accent font-medium hover:underline">
            Logs
          </Link>
          .
        </p>
      </Section>

      <Section id="dashboard" title="Dashboard">
        <p>
          The Dashboard lists trades that are <strong className="text-foreground">ACTIVE</strong> in the database and
          not past expiry. Summary tiles show how many trades exist, how many are being price-tracked, and how many have
          enough history for analysis.
        </p>
        <p>
          <strong className="text-foreground">Sync from Sheet</strong> pulls the latest rows from your Google Sheet
          into the app (updates take-profit text, adds new trades where appropriate).{" "}
          <strong className="text-foreground">Date filters</strong> and column modes (All / Current / Babji) help you
          focus the table.
        </p>
        <p>
          Columns include <strong className="text-foreground">Entry</strong>,{" "}
          <strong className="text-foreground">Take Profits</strong>, <strong className="text-foreground">Current Price</strong>{" "}
          (last quote the app received), <strong className="text-foreground">Drawdown</strong> from entry using current
          price, and more — explained in the sections below.
        </p>
      </Section>

      <Section id="tp1" title="TP1 & take profits">
        <p>
          <strong className="text-foreground">TP1</strong> is the <em>first</em> take-profit <em>price above your
          entry</em>, using the <em>order</em> of targets as they appear on the sheet. If the sheet lists targets out of
          numeric order, TP1 still follows <em>sheet order</em>, not smallest dollar first.
        </p>
        <p>
          <strong className="text-foreground">TP2, TP3, …</strong> are the next targets above entry in that same order.
          The expandable per-TP lines on the Dashboard show, for each level, the worst drawdown in the window{" "}
          <em>from first tracking until the first time price reaches that level</em> (see below).
        </p>
        <p>
          If the Take Profits column is empty, there is no TP1 — Babji-style metrics are not applicable; use{" "}
          <strong className="text-foreground">Current DD %</strong> only.
        </p>
      </Section>

      <Section id="drawdowns" title="Current DD % vs Babji DD %">
        <p>
          <strong className="text-foreground">Current DD %</strong> is based on the{" "}
          <strong className="text-foreground">lowest option price</strong> seen since tracking started, compared to
          entry. It is a <em>global</em> “worst since we started watching” number. If price dips again after TP1, that
          can still affect Current DD %.
        </p>
        <p>
          <strong className="text-foreground">Babji DD %</strong> answers a different question:{" "}
          <em>How much heat did you take before first reaching TP1?</em> It uses only prices{" "}
          <strong className="text-foreground">up to the first time</strong> the quote reaches TP1. After TP1 is
          touched, that drawdown value is <strong className="text-foreground">frozen</strong> — it does not add deeper
          losses that happen later. So Babji DD is the right metric when you are reasoning about stops relative to
          “making it to TP1.”
        </p>
        <p>
          The app builds that path from <strong className="text-foreground">price history</strong> (logged quotes). If
          you enter a manual <strong className="text-foreground">Lowest Price Before TP1</strong> on the sheet for a
          trade without full logs, that value can be used instead.
        </p>
      </Section>

      <Section id="sources" title="Live, Frozen, Limited, and N/A (Source)">
        <ul className="list-disc pl-5 space-y-2">
          <li>
            <strong className="text-foreground">Live</strong> — TP1 exists but has not been hit yet. Babji DD uses the
            running minimum price so far (still “before TP1” by definition).
          </li>
          <li>
            <strong className="text-foreground">Frozen</strong> — TP1 was hit. Babji DD is locked to the worst
            drawdown before that moment.
          </li>
          <li>
            <strong className="text-foreground">Limited</strong> — TP1 was hit, but the stored history does not show an
            earlier dip (e.g. the first stored quote was already at or past TP1). The drawdown shows 0% with a limited
            history warning.
          </li>
          <li>
            <strong className="text-foreground">N/A</strong> — No take-profit targets, so “before TP1” is undefined for
            Babji; use Current DD %.
          </li>
        </ul>
        <p className="pt-1">
          Amber styling on price sometimes means <strong className="text-foreground">no quote yet</strong> for that
          cycle — not that the math is wrong.
        </p>
      </Section>

      <Section id="analysis" title="Analysis & recommended stop">
        <p>
          The{" "}
          <Link to="/analysis" className="text-accent font-medium hover:underline">
            Analysis
          </Link>{" "}
          page looks at trades tracked for at least the configured number of days (often 7) and that have{" "}
          <strong className="text-foreground">reached TP1</strong>. For each, it uses the{" "}
          <strong className="text-foreground">drawdown before TP1</strong> (same idea as Babji — worst move before first
          touch of TP1), not the current price.
        </p>
        <p>
          It then <strong className="text-foreground">simulates</strong> fixed stop levels:{" "}
          <strong className="text-foreground">15%, 20%, 25%, 30%, 35%, 40%</strong> (of entry). For each level, it
          counts how many of those trades would have been “stopped out” before TP1 if you had used that rule.
        </p>
        <p>
          The <strong className="text-foreground">recommended stop</strong> picks the{" "}
          <em>tightest</em> tested stop whose stop-out rate is <strong className="text-foreground">under 50%</strong> of
          the included trades. If every level would stop out half or more, the tool falls back to{" "}
          <strong className="text-foreground">30%</strong> as a middle default — you should still read the table and
          sample size on the page.
        </p>
        <p>
          Very deep “lotto-style” trades (signed drawdown below a threshold, often around{" "}
          <strong className="text-foreground">−70%</strong>) can be excluded from the stop simulation so a few extreme
          names do not dominate the counts — the Analysis page mentions when that happens.
        </p>
      </Section>

      <Section id="sheet-ref" title="Sheet Reference">
        <p>
          <Link to="/sheet-reference" className="text-accent font-medium hover:underline">
            Sheet Reference
          </Link>{" "}
          shows rows from your Google Sheet and explains why each appears as{" "}
          <strong className="text-foreground">on the dashboard</strong>, skipped (expired, parse issue, etc.), or
          otherwise. Use it when a trade is missing from the Dashboard or when sheet columns do not match what you
          expect.
        </p>
      </Section>

      <Section id="logs" title="Logs">
        <p>
          <Link to="/logs" className="text-accent font-medium hover:underline">
            Logs
          </Link>{" "}
          surfaces recent application log lines for troubleshooting (sync, API, scheduler). It is aimed at operators and
          support, not at trading signals.
        </p>
      </Section>

      <section
        id="disclaimer"
        className="scroll-mt-24 rounded-xl border border-amber-500/30 bg-amber-500/5 p-5 sm:p-6"
      >
        <h2 className="text-lg font-semibold text-foreground">Important caveat</h2>
        <p className="mt-3 text-sm text-muted-foreground leading-relaxed">
          This tool is for measurement and discussion based on <em>your</em> sheet and logged prices. It is not
          investment advice. Past drawdowns and recommended stops do not guarantee future results. Position sizing, risk
          tolerance, and your own rules always come first.
        </p>
      </section>

      <p className="text-xs text-muted-foreground pb-4">
        Questions about a specific row? Check the Take Profits column, then compare{" "}
        <strong className="text-foreground">Current DD %</strong> (global worst since tracking) and{" "}
        <strong className="text-foreground">Babji DD %</strong> (worst before TP1 only, when TP1 exists).
      </p>
    </div>
  );
}
