import os
import time
from typing import Dict, List, Tuple

import httpx


class WebSearchService:
    """Brave Search API wrapper with structured summary output."""

    def __init__(self, client: httpx.AsyncClient | None = None):
        self.api_key = os.getenv("BRAVE_API_KEY", "")
        self.base_url = os.getenv("BRAVE_SEARCH_URL", "https://api.search.brave.com/res/v1/web/search")
        self.timeout_seconds = float(os.getenv("WEB_SEARCH_TIMEOUT_SECONDS", "8"))
        ttl_raw = int(os.getenv("WEB_SEARCH_CACHE_TTL_SECONDS", "600"))
        self.cache_ttl_seconds = max(300, min(ttl_raw, 900))

        self._client = client
        self._cache: Dict[Tuple[str, int], Dict] = {}

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout_seconds)
        return self._client

    def _cache_key(self, query: str, count: int) -> Tuple[str, int]:
        return (query.strip().lower(), count)

    def _get_cached(self, key: Tuple[str, int]) -> Dict | None:
        cached = self._cache.get(key)
        if not cached:
            return None

        if time.time() - cached["cached_at"] > self.cache_ttl_seconds:
            return None

        data = dict(cached["data"])
        data["source"] = "cache"
        return data

    def _set_cache(self, key: Tuple[str, int], data: Dict):
        self._cache[key] = {"cached_at": time.time(), "data": dict(data)}

    async def search(self, query: str, count: int = 5) -> Dict:
        if not query.strip():
            raise ValueError("query is required")
        if not self.api_key:
            raise RuntimeError("BRAVE_API_KEY is not configured")

        count = max(1, min(count, 10))
        cache_key = self._cache_key(query, count)
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        client = self._get_client()
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.api_key,
        }
        params = {"q": query, "count": count}

        try:
            response = await client.get(self.base_url, headers=headers, params=params, timeout=self.timeout_seconds)
            response.raise_for_status()
        except (httpx.TimeoutException, httpx.HTTPError):
            stale = self._cache.get(cache_key)
            if stale:
                degraded = dict(stale["data"])
                degraded["source"] = "stale_cache"
                degraded["degraded"] = True
                return degraded
            return {
                "query": query,
                "total": 0,
                "top_result": None,
                "results": [],
                "source": "degraded_empty",
                "degraded": True,
            }

        payload = response.json()
        raw_results = payload.get("web", {}).get("results", [])
        results: List[Dict] = []
        for item in raw_results:
            results.append(
                {
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("description", ""),
                }
            )

        summary = {
            "query": query,
            "total": len(results),
            "top_result": results[0] if results else None,
            "results": results,
            "source": "api",
        }
        self._set_cache(cache_key, summary)
        return summary
