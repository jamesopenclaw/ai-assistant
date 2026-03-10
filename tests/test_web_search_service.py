import pytest
import httpx

from app.services.web_search_service import WebSearchService


@pytest.mark.asyncio
async def test_web_search_structured_summary(monkeypatch):
    monkeypatch.setenv("BRAVE_API_KEY", "test-key")

    async def handler(request: httpx.Request):
        return httpx.Response(
            200,
            json={
                "web": {
                    "results": [
                        {
                            "title": "Result A",
                            "url": "https://example.com/a",
                            "description": "Snippet A",
                        },
                        {
                            "title": "Result B",
                            "url": "https://example.com/b",
                            "description": "Snippet B",
                        },
                    ]
                }
            },
        )

    transport = httpx.MockTransport(handler)
    client = httpx.AsyncClient(transport=transport)
    service = WebSearchService(client=client)

    result = await service.search("python", count=2)
    assert result["query"] == "python"
    assert result["total"] == 2
    assert result["top_result"]["title"] == "Result A"
    assert result["results"][1]["url"] == "https://example.com/b"
    assert result["source"] == "api"


@pytest.mark.asyncio
async def test_web_search_cache_hit(monkeypatch):
    monkeypatch.setenv("BRAVE_API_KEY", "test-key")

    state = {"calls": 0}

    async def handler(request: httpx.Request):
        state["calls"] += 1
        return httpx.Response(
            200,
            json={
                "web": {
                    "results": [
                        {
                            "title": "Cached Result",
                            "url": "https://example.com/cached",
                            "description": "Snippet",
                        }
                    ]
                }
            },
        )

    transport = httpx.MockTransport(handler)
    client = httpx.AsyncClient(transport=transport)
    service = WebSearchService(client=client)

    first = await service.search("cache me", count=1)
    second = await service.search("cache me", count=1)

    assert first["source"] == "api"
    assert second["source"] == "cache"
    assert state["calls"] == 1


@pytest.mark.asyncio
async def test_web_search_timeout_degrade_with_stale_cache(monkeypatch):
    monkeypatch.setenv("BRAVE_API_KEY", "test-key")

    async def ok_handler(request: httpx.Request):
        return httpx.Response(
            200,
            json={
                "web": {
                    "results": [
                        {
                            "title": "Warm Cache",
                            "url": "https://example.com/warm",
                            "description": "Warm",
                        }
                    ]
                }
            },
        )

    ok_client = httpx.AsyncClient(transport=httpx.MockTransport(ok_handler))
    service = WebSearchService(client=ok_client)
    await service.search("stale", count=1)
    key = service._cache_key("stale", 1)
    service._cache[key]["cached_at"] -= service.cache_ttl_seconds + 1

    async def timeout_handler(request: httpx.Request):
        raise httpx.ReadTimeout("timeout")

    service._client = httpx.AsyncClient(transport=httpx.MockTransport(timeout_handler))
    result = await service.search("stale", count=1)

    assert result["degraded"] is True
    assert result["source"] == "stale_cache"
    assert result["total"] == 1


@pytest.mark.asyncio
async def test_web_search_count_is_clamped(monkeypatch):
    monkeypatch.setenv("BRAVE_API_KEY", "test-key")
    called = {"count": None}

    async def handler(request: httpx.Request):
        called["count"] = request.url.params.get("count")
        return httpx.Response(200, json={"web": {"results": []}})

    service = WebSearchService(client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))

    await service.search("python", count=0)
    assert called["count"] == "1"

    await service.search("python max", count=99)
    assert called["count"] == "10"


@pytest.mark.asyncio
async def test_web_search_empty_query_raises(monkeypatch):
    monkeypatch.setenv("BRAVE_API_KEY", "test-key")
    service = WebSearchService(client=httpx.AsyncClient(transport=httpx.MockTransport(lambda req: httpx.Response(200))))

    with pytest.raises(ValueError, match="query is required"):
        await service.search("   ")


@pytest.mark.asyncio
async def test_web_search_missing_api_key_raises(monkeypatch):
    monkeypatch.delenv("BRAVE_API_KEY", raising=False)
    service = WebSearchService(client=httpx.AsyncClient(transport=httpx.MockTransport(lambda req: httpx.Response(200))))

    with pytest.raises(RuntimeError, match="BRAVE_API_KEY is not configured"):
        await service.search("python")


@pytest.mark.asyncio
async def test_web_search_http_error_degrade_to_empty(monkeypatch):
    monkeypatch.setenv("BRAVE_API_KEY", "test-key")

    async def handler(request: httpx.Request):
        return httpx.Response(503, json={"error": "unavailable"})

    service = WebSearchService(client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))
    result = await service.search("python")

    assert result["degraded"] is True
    assert result["source"] == "degraded_empty"
    assert result["total"] == 0
