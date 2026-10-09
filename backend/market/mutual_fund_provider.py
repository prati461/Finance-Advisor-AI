"""
Indian Mutual Fund Data Provider

Fetches official AMFI Indian Mutual Fund NAV data and scheme metadata
via the open MFapi.in API (https://api.mfapi.in).

Covers:
- All AMFI-registered mutual fund schemes (>37,000 schemes)
- Direct & Regular plans (Growth, IDCW/Dividend)
- Full daily historical NAV series
- Search by scheme name, AMC keywords, and scheme code
"""

import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
import httpx

from backend.market.cache import market_cache

logger = logging.getLogger(__name__)

MFAPI_BASE_URL = "https://api.mfapi.in/mf"


class MutualFundProvider:
    """Client for Indian Mutual Fund NAV & scheme data."""

    def __init__(self, timeout: float = 12.0):
        self.timeout = timeout

    def search_schemes(self, query: str, limit: int = 25) -> List[Dict[str, Any]]:
        """
        Search mutual fund schemes by scheme name, AMC keyword, or scheme code.
        """
        q = query.strip()
        if not q:
            return []

        cache_key = f"mf:search:{q.lower()}"
        cached = market_cache.get(cache_key)
        if cached is not None:
            return cached[:limit]

        results: List[Dict[str, Any]] = []

        # If user searched directly by scheme code number
        if q.isdigit():
            scheme_data = self.get_scheme_data(int(q))
            if scheme_data and "meta" in scheme_data:
                meta = scheme_data["meta"]
                latest_nav = None
                nav_date = None
                if scheme_data.get("data"):
                    latest_nav = float(scheme_data["data"][0]["nav"])
                    nav_date = scheme_data["data"][0]["date"]
                results.append(
                    {
                        "scheme_code": meta.get("scheme_code"),
                        "scheme_name": meta.get("scheme_name"),
                        "fund_house": meta.get("fund_house"),
                        "scheme_category": meta.get("scheme_category"),
                        "latest_nav": latest_nav,
                        "nav_date": nav_date,
                    }
                )
                market_cache.set(cache_key, results)
                return results

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(f"{MFAPI_BASE_URL}/search", params={"q": q})
                if resp.status_code == 200:
                    raw_items = resp.json() or []
                    for item in raw_items[:limit]:
                        code = item.get("schemeCode")
                        name = item.get("schemeName", "")
                        if code and name:
                            # Parse plan type from name
                            name_upper = name.upper()
                            is_direct = "DIRECT" in name_upper
                            plan = "Direct" if is_direct else "Regular"
                            option = "Growth" if "GROWTH" in name_upper else "IDCW/Div"
                            results.append(
                                {
                                    "scheme_code": code,
                                    "scheme_name": name,
                                    "plan": plan,
                                    "option": option,
                                }
                            )
            market_cache.set(cache_key, results)
            return results[:limit]
        except Exception as exc:
            logger.error("Error searching mutual funds for '%s': %s", q, exc)
            return []

    def get_scheme_data(self, scheme_code: int) -> Optional[Dict[str, Any]]:
        """
        Fetch scheme metadata and complete historical NAV data.
        Cached for 1 hour since AMFI updates NAV once daily after market hours.
        """
        cache_key = f"mf:scheme:{scheme_code}"
        cached = market_cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(f"{MFAPI_BASE_URL}/{scheme_code}")
                if resp.status_code == 200:
                    data = resp.json()
                    if data and "meta" in data and "data" in data and data["data"]:
                        market_cache.set(cache_key, data)
                        return data
                    logger.warning("Scheme %s returned incomplete data: %s", scheme_code, data.get("status"))
                else:
                    logger.warning("Scheme %s HTTP %s: %s", scheme_code, resp.status_code, resp.text[:100])
            return None
        except Exception as exc:
            logger.error("Error fetching scheme %s: %s", scheme_code, exc)
            return None


# Global provider instance
mutual_fund_provider = MutualFundProvider()
