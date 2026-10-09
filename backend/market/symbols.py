"""
Market Symbol Configuration

Centralized registry of all supported financial instruments with their
Yahoo Finance tickers, asset classes, and display metadata.

SYMBOL CATALOG:
- Indices: Nifty 50, Sensex, Bank Nifty
- Commodities: Gold, Silver
- Indian Stocks: Reliance, TCS, Infosys, HDFC Bank, ICICI, SBI, etc.
- ETFs: Nippon India Nifty 50 BeES, Gold BeES, etc.
- US Stocks: AAPL, MSFT, GOOGL, etc.
"""

from typing import Dict, List

# Yahoo Finance symbol (yfinance supports .NS, .BO suffixes for National Stock
# Exchange and Bombay Stock Exchange respectively)
MARKET_SYMBOLS: Dict[str, Dict[str, str]] = {
    # --- Indices ---
    "NIFTY 50": {
        "symbol": "^NSEI",
        "name": "Nifty 50",
        "asset_class": "index",
        "exchange": "NSE",
        "currency": "INR",
    },
    "SENSEX": {
        "symbol": "^BSESN",
        "name": "SENSEX",
        "asset_class": "index",
        "exchange": "BSE",
        "currency": "INR",
    },
    "BANK NIFTY": {
        "symbol": "^NSEBANK",
        "name": "Bank Nifty",
        "asset_class": "index",
        "exchange": "NSE",
        "currency": "INR",
    },
    # --- Commodities ---
    "GOLD": {
        "symbol": "GC=F",
        "name": "Gold Futures",
        "asset_class": "commodity",
        "exchange": "COMEX",
        "currency": "USD",
    },
    "SILVER": {
        "symbol": "SI=F",
        "name": "Silver Futures",
        "asset_class": "commodity",
        "exchange": "COMEX",
        "currency": "USD",
    },
    # --- Top Indian Stocks (NSE) ---
    "RELIANCE": {
        "symbol": "RELIANCE.NS",
        "name": "Reliance Industries",
        "asset_class": "stock",
        "exchange": "NSE",
        "currency": "INR",
        "sector": "Energy",
    },
    "TCS": {
        "symbol": "TCS.NS",
        "name": "Tata Consultancy Services",
        "asset_class": "stock",
        "exchange": "NSE",
        "currency": "INR",
        "sector": "Information Technology",
    },
    "INFY": {
        "symbol": "INFY.NS",
        "name": "Infosys",
        "asset_class": "stock",
        "exchange": "NSE",
        "currency": "INR",
        "sector": "Information Technology",
    },
    "HDFCBANK": {
        "symbol": "HDFCBANK.NS",
        "name": "HDFC Bank",
        "asset_class": "stock",
        "exchange": "NSE",
        "currency": "INR",
        "sector": "Banking",
    },
    "ICICIBANK": {
        "symbol": "ICICIBANK.NS",
        "name": "ICICI Bank",
        "asset_class": "stock",
        "exchange": "NSE",
        "currency": "INR",
        "sector": "Banking",
    },
    "SBIN": {
        "symbol": "SBIN.NS",
        "name": "State Bank of India",
        "asset_class": "stock",
        "exchange": "NSE",
        "currency": "INR",
        "sector": "Banking",
    },
    "ITC": {
        "symbol": "ITC.NS",
        "name": "ITC Limited",
        "asset_class": "stock",
        "exchange": "NSE",
        "currency": "INR",
        "sector": "FMCG",
    },
    "BHARTIARTL": {
        "symbol": "BHARTIARTL.NS",
        "name": "Bharti Airtel",
        "asset_class": "stock",
        "exchange": "NSE",
        "currency": "INR",
        "sector": "Telecom",
    },
    "WIPRO": {
        "symbol": "WIPRO.NS",
        "name": "Wipro",
        "asset_class": "stock",
        "exchange": "NSE",
        "currency": "INR",
        "sector": "Information Technology",
    },
    "AXISBANK": {
        "symbol": "AXISBANK.NS",
        "name": "Axis Bank",
        "asset_class": "stock",
        "exchange": "NSE",
        "currency": "INR",
        "sector": "Banking",
    },
    "HINDUNILVR": {
        "symbol": "HINDUNILVR.NS",
        "name": "Hindustan Unilever",
        "asset_class": "stock",
        "exchange": "NSE",
        "currency": "INR",
        "sector": "FMCG",
    },
    "MARUTI": {
        "symbol": "MARUTI.NS",
        "name": "Maruti Suzuki",
        "asset_class": "stock",
        "exchange": "NSE",
        "currency": "INR",
        "sector": "Automobile",
    },
    "LT": {
        "symbol": "LT.NS",
        "name": "Larsen & Toubro",
        "asset_class": "stock",
        "exchange": "NSE",
        "currency": "INR",
        "sector": "Infrastructure",
    },
    "SUNPHARMA": {
        "symbol": "SUNPHARMA.NS",
        "name": "Sun Pharmaceutical",
        "asset_class": "stock",
        "exchange": "NSE",
        "currency": "INR",
        "sector": "Pharma",
    },
    "TATAMOTORS": {
        "symbol": "TATAMOTORS.NS",
        "name": "Tata Motors",
        "asset_class": "stock",
        "exchange": "NSE",
        "currency": "INR",
        "sector": "Automobile",
    },
    "ASIANPAINT": {
        "symbol": "ASIANPAINT.NS",
        "name": "Asian Paints",
        "asset_class": "stock",
        "exchange": "NSE",
        "currency": "INR",
        "sector": "Consumer",
    },
    "KOTAKBANK": {
        "symbol": "KOTAKBANK.NS",
        "name": "Kotak Mahindra Bank",
        "asset_class": "stock",
        "exchange": "NSE",
        "currency": "INR",
        "sector": "Banking",
    },
    "ULTRACEMCO": {
        "symbol": "ULTRACEMCO.NS",
        "name": "UltraTech Cement",
        "asset_class": "stock",
        "exchange": "NSE",
        "currency": "INR",
        "sector": "Cement",
    },
    "BAJFINANCE": {
        "symbol": "BAJFINANCE.NS",
        "name": "Bajaj Finance",
        "asset_class": "stock",
        "exchange": "NSE",
        "currency": "INR",
        "sector": "NBFC",
    },
    # --- ETFs ---
    "NIFTYBEES": {
        "symbol": "NIFTYBEES.NS",
        "name": "Nippon India Nifty 50 BeES",
        "asset_class": "etf",
        "exchange": "NSE",
        "currency": "INR",
    },
    "GOLDBEES": {
        "symbol": "GOLDBEES.NS",
        "name": "Nippon India Gold BeES",
        "asset_class": "etf",
        "exchange": "NSE",
        "currency": "INR",
    },
    "JUNIORBEES": {
        "symbol": "JUNIORBEES.NS",
        "name": "Nippon India Nifty Next 50 BeES",
        "asset_class": "etf",
        "exchange": "NSE",
        "currency": "INR",
    },
    "NETFAUTO": {
        "symbol": "NETFAUTO.NS",
        "name": "Nifty Auto ETF",
        "asset_class": "etf",
        "exchange": "NSE",
        "currency": "INR",
    },
    # --- US Stocks (optional) ---
    "AAPL": {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "asset_class": "stock",
        "exchange": "NASDAQ",
        "currency": "USD",
        "sector": "Technology",
    },
    "MSFT": {
        "symbol": "MSFT",
        "name": "Microsoft Corp.",
        "asset_class": "stock",
        "exchange": "NASDAQ",
        "currency": "USD",
        "sector": "Technology",
    },
    "GOOGL": {
        "symbol": "GOOGL",
        "name": "Alphabet Inc.",
        "asset_class": "stock",
        "exchange": "NASDAQ",
        "currency": "USD",
        "sector": "Technology",
    },
    "AMZN": {
        "symbol": "AMZN",
        "name": "Amazon.com Inc.",
        "asset_class": "stock",
        "exchange": "NASDAQ",
        "currency": "USD",
        "sector": "Consumer",
    },
    "TSLA": {
        "symbol": "TSLA",
        "name": "Tesla Inc.",
        "asset_class": "stock",
        "exchange": "NASDAQ",
        "currency": "USD",
        "sector": "Automobile",
    },
    "NFLX": {
        "symbol": "NFLX",
        "name": "Netflix Inc.",
        "asset_class": "stock",
        "exchange": "NASDAQ",
        "currency": "USD",
        "sector": "Entertainment",
    },
}


# Known Indian stock sector categorization for sector-performance analysis
INDIAN_STOCKS: List[str] = [
    "RELIANCE",
    "TCS",
    "INFY",
    "HDFCBANK",
    "ICICIBANK",
    "SBIN",
    "ITC",
    "BHARTIARTL",
    "WIPRO",
    "AXISBANK",
    "HINDUNILVR",
    "MARUTI",
    "LT",
    "SUNPHARMA",
    "TATAMOTORS",
    "ASIANPAINT",
    "KOTAKBANK",
    "ULTRACEMCO",
    "BAJFINANCE",
]

# Common NSE mutual fund family (direct/growth plans) approximated via
# underlying ETFs or index proxies where possible. This list is used for
# the mutual fund analyzer with fallback to NAV-based computation.
MUTUAL_FUNDS: Dict[str, Dict[str, str]] = {
    "NIFTY 50 INDEX FUND": {
        "symbol": "NIFTYBEES.NS",
        "name": "Nifty 50 Index Fund",
        "category": "Index Fund",
        "proxy": "NIFTYBEES.NS",
    },
    "SENSEX INDEX FUND": {
        "symbol": "^BSESN",
        "name": "Sensex Index Fund",
        "category": "Index Fund",
        "proxy": "^BSESN",
    },
    "GOLD FUND": {
        "symbol": "GOLDBEES.NS",
        "name": "Gold Fund",
        "category": "Commodity",
        "proxy": "GOLDBEES.NS",
    },
    "BANKING FUND": {
        "symbol": "^NSEBANK",
        "name": "Banking & Financial Services Fund",
        "category": "Sectoral",
        "proxy": "^NSEBANK",
    },
    "MIDCAP FUND": {
        "symbol": "JUNIORBEES.NS",
        "name": "Mid Cap Fund",
        "category": "Equity Mid Cap",
        "proxy": "JUNIORBEES.NS",
    },
    "IT FUND": {
        "symbol": "INFY.NS",
        "name": "Information Technology Fund",
        "category": "Sectoral",
        "proxy": "INFY.NS",
    },
}


COMMON_ALIASES: Dict[str, str] = {
    "^NSEI": "NIFTY 50",
    "NIFTY": "NIFTY 50",
    "NIFTY 50": "NIFTY 50",
    "NIFTY50": "NIFTY 50",
    "NSEI": "NIFTY 50",
    "^BSESN": "SENSEX",
    "SENSEX": "SENSEX",
    "BSESN": "SENSEX",
    "BSE": "SENSEX",
    "BSE SENSEX": "SENSEX",
    "^NSEBANK": "BANK NIFTY",
    "BANK NIFTY": "BANK NIFTY",
    "BANKNIFTY": "BANK NIFTY",
    "NIFTYBANK": "BANK NIFTY",
    "NIFTY BANK": "BANK NIFTY",
    "NSEBANK": "BANK NIFTY",
    "GC=F": "GOLD",
    "GOLD": "GOLD",
    "GOLD FUTURES": "GOLD",
    "SI=F": "SILVER",
    "SILVER": "SILVER",
    "SILVER FUTURES": "SILVER",
}


def get_symbol_info(query: str) -> Dict[str, str]:
    """Resolve a user query to symbol info (case-insensitive)."""
    q = query.upper().strip()

    # 1. Direct alias check
    if q in COMMON_ALIASES and COMMON_ALIASES[q] in MARKET_SYMBOLS:
        return dict(MARKET_SYMBOLS[COMMON_ALIASES[q]])

    # 2. Direct key in MARKET_SYMBOLS
    if q in MARKET_SYMBOLS:
        return dict(MARKET_SYMBOLS[q])

    # 3. Exact match on Yahoo provider symbol (e.g. ^NSEI, GC=F, RELIANCE.NS)
    for key, info in MARKET_SYMBOLS.items():
        if q == info.get("symbol", "").upper():
            return dict(info)

    # 4. Suffix stripped match (e.g. RELIANCE.NS -> RELIANCE)
    if q.endswith((".NS", ".BO")):
        stem = q[:-3]
        if stem in MARKET_SYMBOLS:
            return dict(MARKET_SYMBOLS[stem])

    # 5. Fuzzy match on key or full name
    for key, info in MARKET_SYMBOLS.items():
        if q == key or q in key or q in info.get("name", "").upper():
            return dict(info)

    # 6. Treat as raw ticker without corrupting futures or index symbols
    is_special = q.startswith("^") or "=" in q or q.endswith((".NS", ".BO"))
    suffix = "" if is_special else ".NS"
    return {
        "symbol": q + suffix,
        "name": q,
        "asset_class": "commodity" if "=" in q else "index" if q.startswith("^") else "stock",
        "exchange": "NSE" if suffix == ".NS" else "UNKNOWN",
        "currency": "USD" if "=" in q else "INR",
    }

