"""
Market data API: Massive, Finnhub, Alpha Vantage, or Tradier.
Option chain, contract resolution (cached), live quote.

Tradier: Bearer token, GET /markets/quotes?symbols=OCC (OCC format).
Alpha Vantage: function=REALTIME_OPTIONS, symbol, contract (OCC format).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests

from . import config

logger = logging.getLogger(__name__)


@dataclass
class OptionContract:
    symbol: str
    ticker: str
    strike: float
    expiry: str
    type: str


class APIError(Exception):
    pass


class MarketDataAPI:
    def __init__(self, base_url: str = "", api_key: str = "", mock: bool = False):
        self.base_url = (base_url or config.API_BASE_URL).rstrip("/")
        self.api_key = (api_key or config.API_KEY).strip()
        self.mock = mock or config.MOCK_API
        self._provider = getattr(config, "API_PROVIDER", "massive")
        self._contract_cache: Dict[str, OptionContract] = {}

    def _auth_param(self) -> str:
        """Param name for auth: Massive apiKey, Finnhub token, Alpha Vantage apikey. Tradier uses Bearer header."""
        if self._provider in ("alphavantage",):
            return "apikey"
        if self._provider == "massive":
            return "apiKey"
        if self._provider == "tradier":
            return "_bearer"  # special: use header, not param
        return "token"

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        use_auth: bool = True,
    ) -> Dict[str, Any]:
        if self.mock:
            raise APIError("Mock mode: no HTTP")
        if not self.api_key:
            raise APIError("API_KEY not set")
        url = f"{self.base_url}/{path.lstrip('/')}"
        params = dict(params or {})
        headers: Dict[str, str] = {"Accept": "application/json"}
        if use_auth:
            if self._provider == "tradier":
                headers["Authorization"] = f"Bearer {self.api_key}"
            else:
                params[self._auth_param()] = self.api_key
        try:
            r = requests.request(method, url, params=params, headers=headers, timeout=30)
        except requests.RequestException as e:
            raise APIError(f"Request failed: {e}")
        if r.status_code == 429:
            raise APIError("Rate limit (429)")
        try:
            data = r.json()
        except ValueError as e:
            body = (r.text or "")[:500]
            preview = body.replace("\n", " ").strip()
            logger.warning(
                "API returned non-JSON (status=%s, url=%s): %s",
                r.status_code, url, preview or "(empty body)"
            )
            raise APIError(
                f"Invalid JSON response (HTTP {r.status_code}): {preview[:200] or 'empty body'}"
            ) from e
        if not r.ok:
            err = data.get("message", data.get("error_message", r.text[:200])) if isinstance(data, dict) else r.text[:200]
            raise APIError(f"HTTP {r.status_code}: {err}")
        # Alpha Vantage error in 200 body
        if isinstance(data, dict) and data.get("Note"):
            raise APIError(f"Alpha Vantage: {data['Note']}")
        if isinstance(data, dict) and "Error Message" in data:
            raise APIError(f"Alpha Vantage: {data['Error Message']}")
        return data

    # ---- Massive API (default) ----

    def _get_option_chain_massive(
        self, ticker: str, expiry: str, contract_type: str = "", strike_price: float = 0
    ) -> Dict[str, Any]:
        """GET /v3/snapshot/options/{underlyingAsset} with filters (expiration_date, contract_type, strike_price)."""
        params: Dict[str, Any] = {"limit": 250, "order": "asc", "sort": "ticker"}
        if expiry:
            params["expiration_date"] = expiry[:10]
        if contract_type:
            params["contract_type"] = contract_type
        if strike_price and strike_price > 0:
            params["strike_price"] = strike_price
        return self._request("GET", f"/v3/snapshot/options/{ticker.upper()}", params)

    def _extract_options_massive(self, resp: Dict[str, Any]) -> list:
        """Parse Massive option chain: results[] with details.ticker, details.strike_price, etc."""
        if not isinstance(resp, dict):
            return []
        results = resp.get("results")
        if isinstance(results, list):
            return results
        return []

    def _find_contract_massive(
        self, ticker: str, strike: float, expiry: str, option_type: str
    ) -> Optional[OptionContract]:
        ct = "call" if option_type.upper() in ("CALL", "C") else "put"
        resp = self._get_option_chain_massive(ticker, expiry, contract_type=ct, strike_price=strike)
        options = self._extract_options_massive(resp)
        expiry_norm = (expiry or "")[:10]
        for opt in options:
            details = opt.get("details") or {}
            sym = details.get("ticker") or opt.get("ticker")
            sp = details.get("strike_price")
            exp = details.get("expiration_date") or opt.get("expiration_date")
            raw_ct = (details.get("contract_type") or opt.get("contract_type") or "").lower()
            opt_ct = "call" if raw_ct in ("c", "call") else "put" if raw_ct in ("p", "put") else raw_ct
            try:
                sp_val = float(sp) if sp is not None else 0
            except (TypeError, ValueError):
                continue
            exp_norm = (str(exp) or "")[:10]
            if (
                opt_ct == ct
                and abs(sp_val - strike) < 1e-6
                and (not expiry_norm or not exp_norm or exp_norm == expiry_norm)
                and sym
            ):
                quote_sym = sym if str(sym).startswith("O:") else f"O:{sym}"
                return OptionContract(
                    symbol=quote_sym,
                    ticker=ticker,
                    strike=sp_val,
                    expiry=expiry,
                    type=option_type.upper(),
                )
        logger.debug(
            "Massive: no matching contract for %s %s %s %s (got %d options)",
            ticker, strike, expiry, option_type, len(options),
        )
        return None

    def _get_option_quote_massive(self, symbol: str) -> Optional[float]:
        """GET /v2/last/trade/{optionsTicker} -> results.p"""
        resp = self._request("GET", f"/v2/last/trade/{symbol}")
        results = resp.get("results") if isinstance(resp.get("results"), dict) else None
        if not results:
            return None
        p = results.get("p")
        if p is None:
            return None
        try:
            return float(p)
        except (TypeError, ValueError):
            return None

    # ---- Finnhub API (legacy) ----

    def _get_option_chain_finnhub(self, ticker: str, expiry: str) -> Dict[str, Any]:
        return self._request("GET", "/stock/option-chain", {"symbol": ticker, "date": expiry})

    def _extract_options_finnhub(self, chain: Dict[str, Any]) -> list:
        if not isinstance(chain, dict):
            return []
        out: list = []
        data = chain.get("data")
        if isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    continue
                opts = item.get("options")
                if isinstance(opts, dict):
                    out.extend(opts.get("calls") or opts.get("CALL") or [])
                    out.extend(opts.get("puts") or opts.get("PUT") or [])
                elif isinstance(opts, list):
                    out.extend(opts)
            if out:
                return out
        if isinstance(data, dict):
            opts = data.get("options")
            if isinstance(opts, dict):
                out.extend(opts.get("calls") or opts.get("CALL") or [])
                out.extend(opts.get("puts") or opts.get("PUT") or [])
        result = chain.get("result")
        if isinstance(result, dict):
            opts = result.get("options")
            if isinstance(opts, dict):
                out.extend(opts.get("calls") or opts.get("CALL") or [])
                out.extend(opts.get("puts") or opts.get("PUT") or [])
        opts = chain.get("options")
        if isinstance(opts, dict):
            out.extend(opts.get("calls") or opts.get("CALL") or [])
            out.extend(opts.get("puts") or opts.get("PUT") or [])
        elif isinstance(opts, list):
            return opts
        return out

    def _find_contract_finnhub(
        self, ticker: str, strike: float, expiry: str, option_type: str
    ) -> Optional[OptionContract]:
        chain = self._get_option_chain_finnhub(ticker, expiry)
        options_list = self._extract_options_finnhub(chain)
        if not options_list:
            logger.debug("Finnhub: no options for %s %s", ticker, expiry)
            return None
        ot = "CALL" if option_type.upper() in ("CALL", "C") else "PUT"
        expiry_norm = (expiry or "")[:10]
        for opt in options_list:
            try:
                raw_type = str(opt.get("type") or opt.get("optionType") or "").upper()
                opt_type = "CALL" if raw_type in ("C", "CALL") else "PUT" if raw_type in ("P", "PUT") else raw_type
                opt_strike = float(opt.get("strike") or opt.get("strikePrice") or 0)
                exp = str(opt.get("expirationDate") or opt.get("expiry") or opt.get("expiration_date") or "")
                exp_norm = exp[:10] if exp else ""
                sym = opt.get("contractName") or opt.get("symbol") or opt.get("contractSymbol") or opt.get("contract")
            except (TypeError, ValueError):
                continue
            if opt_type != ot or abs(opt_strike - strike) > 1e-6 or (exp_norm and expiry_norm and exp_norm != expiry_norm):
                continue
            if not sym:
                continue
            quote_symbol = sym if str(sym).startswith("O:") else f"O:{sym}"
            return OptionContract(symbol=quote_symbol, ticker=ticker, strike=opt_strike, expiry=expiry, type=ot)
        logger.debug("Finnhub: no match for %s %s %s %s", ticker, strike, expiry, option_type)
        return None

    def _get_option_quote_finnhub(self, symbol: str) -> Optional[float]:
        data = self._request("GET", "/quote", {"symbol": symbol})
        c = data.get("c")
        if c is None:
            return None
        try:
            return float(c)
        except (TypeError, ValueError):
            return None

    # ---- Alpha Vantage API ----

    @staticmethod
    def _build_occ_symbol(ticker: str, expiry: str, option_type: str, strike: float) -> str:
        """Build OCC option symbol: IBM270115C00390000."""
        yymmdd = (expiry or "")[:10].replace("-", "")[2:8]  # YYYYMMDD -> YYMMDD
        if len(yymmdd) != 6:
            yymmdd = "000000"
        ct = "C" if (option_type or "").upper() in ("CALL", "C") else "P"
        strike_int = int(round(float(strike) * 1000))
        strike_str = str(strike_int).zfill(8)
        return f"{ticker.upper()}{yymmdd}{ct}{strike_str}"

    def _get_realtime_options_alphavantage(
        self, ticker: str, contract: Optional[str] = None
    ) -> Dict[str, Any]:
        """GET /query?function=REALTIME_OPTIONS&symbol=X&apikey=... Optional: contract=OCC."""
        params: Dict[str, Any] = {
            "function": "REALTIME_OPTIONS",
            "symbol": ticker.upper(),
        }
        if contract:
            params["contract"] = contract
        return self._request("GET", "/query", params)

    def _extract_options_alphavantage(self, resp: Dict[str, Any]) -> list:
        """Parse Alpha Vantage option chain. Handles chain/optionChain/data structures."""
        if not isinstance(resp, dict):
            return []
        for key in ("chain", "optionChain", "data", "options"):
            val = resp.get(key)
            if isinstance(val, list):
                return val
            if isinstance(val, dict) and "chain" in val:
                return val.get("chain") or []
        # Flat structure: expirations -> options per expiry
        expirations = resp.get("expirations") or resp.get("expirationDates") or []
        out: list = []
        for exp in expirations if isinstance(expirations, list) else []:
            opts = exp.get("options") or exp.get("calls") or exp.get("puts") if isinstance(exp, dict) else []
            if isinstance(opts, list):
                out.extend(opts)
        return out

    def _find_contract_alphavantage(
        self, ticker: str, strike: float, expiry: str, option_type: str
    ) -> Optional[OptionContract]:
        """Build OCC symbol and return contract. Alpha Vantage uses OCC format."""
        occ = self._build_occ_symbol(ticker, expiry, option_type, strike)
        try:
            resp = self._get_realtime_options_alphavantage(ticker, contract=occ)
        except APIError:
            return None
        # If we got a response, contract exists. Return OptionContract with OCC symbol.
        ot = "CALL" if (option_type or "").upper() in ("CALL", "C") else "PUT"
        return OptionContract(
            symbol=f"O:{occ}",
            ticker=ticker,
            strike=strike,
            expiry=expiry or "",
            type=ot,
        )

    # ---- Tradier API ----

    def _find_contract_tradier(
        self, ticker: str, strike: float, expiry: str, option_type: str
    ) -> Optional[OptionContract]:
        """Tradier uses OCC symbol format. Build it directly; no chain fetch needed."""
        occ = self._build_occ_symbol(ticker, expiry, option_type, strike)
        ot = "CALL" if (option_type or "").upper() in ("CALL", "C") else "PUT"
        return OptionContract(
            symbol=occ,  # Tradier expects raw OCC, no O: prefix
            ticker=ticker,
            strike=strike,
            expiry=expiry or "",
            type=ot,
        )

    def _get_option_quote_tradier(self, symbol: str) -> Optional[float]:
        """Tradier: GET /markets/quotes?symbols=OCC. Response: quotes.quote with last, bid, ask."""
        occ = (symbol or "").replace("O:", "").strip()
        if not occ:
            return None
        resp = self._request("GET", "/markets/quotes", {"symbols": occ})
        quotes = resp.get("quotes") or resp
        quote = quotes.get("quote") if isinstance(quotes, dict) else None
        if quote is None:
            logger.warning("Tradier API: no quote for %s", occ)
            return None
        if isinstance(quote, list):
            quote = quote[0] if quote else {}
        last_v = quote.get("last") if isinstance(quote, dict) else None
        close_v = quote.get("close") if isinstance(quote, dict) else None
        bid_v = quote.get("bid") if isinstance(quote, dict) else None
        ask_v = quote.get("ask") if isinstance(quote, dict) else None
        logger.info(
            "API [Tradier] option %s: last=%s close=%s bid=%s ask=%s",
            occ, last_v, close_v, bid_v, ask_v,
        )
        for v in (last_v, close_v, bid_v, ask_v):
            if v is not None:
                try:
                    price = float(v)
                    logger.info("API [Tradier] using price $%.2f for %s", price, occ)
                    return price
                except (TypeError, ValueError):
                    pass
        logger.warning("API [Tradier] no valid price for %s", occ)
        return None

    # ---- Alpha Vantage API ----

    def _get_option_quote_alphavantage(self, symbol: str) -> Optional[float]:
        """Alpha Vantage: use contract param with OCC symbol (strip O: prefix if present)."""
        occ = symbol.replace("O:", "").strip() if symbol else ""
        if not occ:
            return None
        # OCC: IBM270115C00390000 -> ticker=IBM (letters before first digit)
        i = 0
        while i < len(occ) and occ[i].isalpha():
            i += 1
        ticker = occ[:i] if i > 0 else occ[:4]
        resp = self._get_realtime_options_alphavantage(ticker, contract=occ)
        for key in ("last", "close", "price", "bid", "ask", "mark"):
            v = resp.get(key) if isinstance(resp, dict) else None
            if v is not None:
                try:
                    return float(v)
                except (TypeError, ValueError):
                    pass
        return None

    # ---- Unified interface ----

    def find_contract(
        self,
        ticker: str,
        strike: float,
        expiry: str,
        option_type: str,
    ) -> Optional[OptionContract]:
        key = f"{ticker}|{strike}|{expiry}|{option_type.upper()}"
        if key in self._contract_cache:
            return self._contract_cache[key]
        if self.mock:
            c = OptionContract(
                symbol=f"O:{ticker}{(expiry or '').replace('-','')[:8]}C{int(strike)}"
                if "C" in (option_type or "").upper()
                else f"O:{ticker}{(expiry or '').replace('-','')[:8]}P{int(strike)}",
                ticker=ticker,
                strike=strike,
                expiry=expiry or "",
                type=(option_type or "CALL").upper(),
            )
            self._contract_cache[key] = c
            return c
        if self._provider == "alphavantage":
            c = self._find_contract_alphavantage(ticker, strike, expiry, option_type)
        elif self._provider == "tradier":
            c = self._find_contract_tradier(ticker, strike, expiry, option_type)
        elif self._provider == "massive":
            c = self._find_contract_massive(ticker, strike, expiry, option_type)
        else:
            c = self._find_contract_finnhub(ticker, strike, expiry, option_type)
        if c:
            self._contract_cache[key] = c
        return c

    def get_option_quote(self, symbol: str) -> Optional[float]:
        if self.mock:
            return 2.5
        if self._provider == "alphavantage":
            return self._get_option_quote_alphavantage(symbol)
        if self._provider == "tradier":
            return self._get_option_quote_tradier(symbol)
        if self._provider == "massive":
            return self._get_option_quote_massive(symbol)
        return self._get_option_quote_finnhub(symbol)
