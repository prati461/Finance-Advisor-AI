"""
Integration and unit tests for Stock Market symbols, providers,
and Indian Mutual Fund analytics via AMFI/MFapi.
"""
import pytest
from backend.market.symbols import get_symbol_info, COMMON_ALIASES
from backend.market.manager import market_data_manager
from backend.ml.services.mutual_fund_service import mutual_fund_service
from backend.market.mutual_fund_provider import mutual_fund_provider


def test_market_symbol_mapping_exact_and_aliases():
    """Verify that Yahoo symbols, indices, commodities, and Indian stocks resolve correctly without broken .NS suffix."""
    test_cases = [
        ("^NSEI", "^NSEI", "Nifty 50"),
        ("NIFTY 50", "^NSEI", "NIFTY 50"),
        ("^BSESN", "^BSESN", "Sensex"),
        ("SENSEX", "^BSESN", "SENSEX"),
        ("^NSEBANK", "^NSEBANK", "Bank Nifty"),
        ("NIFTYBANK", "^NSEBANK", "NIFTYBANK"),
        ("GC=F", "GC=F", "Gold Futures"),
        ("GOLD", "GC=F", "GOLD"),
        ("SI=F", "SI=F", "Silver Futures"),
        ("SILVER", "SI=F", "SILVER"),
        ("RELIANCE.NS", "RELIANCE.NS", "Reliance Industries"),
        ("TCS.NS", "TCS.NS", "Tata Consultancy Services"),
        ("INFY.NS", "INFY.NS", "Infosys"),
    ]

    for user_input, expected_symbol, _ in test_cases:
        info = get_symbol_info(user_input)
        assert info["symbol"] == expected_symbol, f"Failed for {user_input}: got {info['symbol']}, expected {expected_symbol}"
        assert not info["symbol"].endswith(".NS.NS"), f"Double .NS suffix detected for {user_input}"
        assert not (info["symbol"].startswith("^") and info["symbol"].endswith(".NS")), f"Index corrupted with .NS suffix: {info['symbol']}"
        assert not (info["symbol"].endswith("=F") and info["symbol"].endswith(".NS")), f"Commodity corrupted with .NS suffix: {info['symbol']}"


def test_mutual_fund_curated_and_popular_list():
    """Verify that curated popular funds contain real scheme codes and metadata."""
    funds = mutual_fund_service.list_funds()
    assert len(funds) >= 6
    for fund in funds:
        assert "scheme_code" in fund
        assert fund["scheme_code"] > 0
        assert fund["plan"] in ("Direct", "Regular")
        assert fund["option"] in ("Growth", "IDCW / Dividend")


def test_mutual_fund_search_and_numeric_code():
    """Verify that MFapi search works by name and directly resolves numeric scheme codes."""
    # Search by text
    results = mutual_fund_service.search_funds(query="Parag Parikh", limit=5)
    assert len(results) > 0
    assert any("Parag Parikh" in r["scheme_name"] for r in results)

    # Search by exact numeric code
    direct_code_results = mutual_fund_service.search_funds(query="122639", limit=5)
    assert len(direct_code_results) > 0
    assert direct_code_results[0]["scheme_code"] == 122639


def test_mutual_fund_historical_performance_real_calculations():
    """Verify real returns, CAGR, and downsampled chart points for PPFAS (122639)."""
    perf = mutual_fund_service.get_historical_performance(122639, period="1y")
    assert perf.get("available") is True
    assert perf["scheme_code"] == 122639
    assert perf["latest_nav"] > 0
    assert len(perf["chart_data"]) > 10
    assert perf["percentage_return"] != 0.0
    assert "volatility" in perf
    assert "sharpe_ratio" in perf
    assert "recommendation" in perf
