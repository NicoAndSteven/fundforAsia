from __future__ import annotations
from typing import Optional, List, Dict, Any


class Cache:
    """In-memory cache for API responses."""

    def __init__(self):
        self._prices_cache: Dict[str, List[Dict[str, Any]]] = {}
        self._financial_metrics_cache: Dict[str, List[Dict[str, Any]]] = {}
        self._line_items_cache: Dict[str, List[Dict[str, Any]]] = {}
        self._insider_trades_cache: Dict[str, List[Dict[str, Any]]] = {}
        self._company_news_cache: Dict[str, List[Dict[str, Any]]] = {}
        self._generic_cache: Dict[str, List[Dict[str, Any]]] = {}

    def get(self, cache_type: str, key: str) -> Optional[List[Dict[str, Any]]]:
        """Generic cache get for custom key types."""
        return self._generic_cache.get(f"{cache_type}:{key}")

    def set(self, cache_type: str, key: str, data: List[Dict[str, Any]]):
        """Generic cache set for custom key types."""
        self._generic_cache[f"{cache_type}:{key}"] = data

    def _merge_data(self, existing: Optional[List[Dict]], new_data: List[Dict], key_field: str) -> List[Dict]:
        """Merge existing and new data, avoiding duplicates based on a key field."""
        if not existing:
            return new_data

        existing_keys = {item[key_field] for item in existing}

        merged = existing.copy()
        merged.extend([item for item in new_data if item[key_field] not in existing_keys])
        return merged

    def get_prices(self, ticker: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached price data if available."""
        return self._prices_cache.get(ticker)

    def set_prices(self, ticker: str, data: List[Dict[str, Any]]):
        """Append new price data to cache."""
        self._prices_cache[ticker] = self._merge_data(self._prices_cache.get(ticker), data, key_field="time")

    def get_financial_metrics(self, ticker: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached financial metrics if available."""
        return self._financial_metrics_cache.get(ticker)

    def set_financial_metrics(self, ticker: str, data: List[Dict[str, Any]]):
        """Append new financial metrics to cache."""
        self._financial_metrics_cache[ticker] = self._merge_data(self._financial_metrics_cache.get(ticker), data, key_field="report_period")

    def get_line_items(self, ticker: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached line items if available."""
        return self._line_items_cache.get(ticker)

    def set_line_items(self, ticker: str, data: List[Dict[str, Any]]):
        """Append new line items to cache."""
        self._line_items_cache[ticker] = self._merge_data(self._line_items_cache.get(ticker), data, key_field="report_period")

    def get_insider_trades(self, ticker: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached insider trades if available."""
        return self._insider_trades_cache.get(ticker)

    def set_insider_trades(self, ticker: str, data: List[Dict[str, Any]]):
        """Append new insider trades to cache."""
        self._insider_trades_cache[ticker] = self._merge_data(self._insider_trades_cache.get(ticker), data, key_field="filing_date")

    def get_company_news(self, ticker: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached company news if available."""
        return self._company_news_cache.get(ticker)

    def set_company_news(self, ticker: str, data: List[Dict[str, Any]]):
        """Append new company news to cache."""
        self._company_news_cache[ticker] = self._merge_data(self._company_news_cache.get(ticker), data, key_field="date")


_cache = Cache()


def get_cache() -> Cache:
    """Get the global cache instance."""
    return _cache
