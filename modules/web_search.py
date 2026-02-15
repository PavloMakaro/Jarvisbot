from core.tools import registry
import aiohttp
import config
import logging
import json

logger = logging.getLogger(__name__)

@registry.register(name="web_search", description="Search the web for information using LangSearch.")
async def web_search(query: str, max_results: int = 5, freshness: str = None):
    logger.info(f"Searching web for: {query}")

    api_url = "https://api.langsearch.com/v1/web-search"
    headers = {
        "Authorization": f"Bearer {config.LANGSEARCH_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "query": query,
        "count": max_results,
        "summary": True
    }

    if freshness:
        payload["freshness"] = freshness

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, headers=headers, json=payload) as response:
                if response.status != 200:
                    text = await response.text()
                    logger.error(f"LangSearch API Error: {response.status} - {text}")
                    return f"Search failed. API returned status {response.status}."

                data = await response.json()
                logger.info(f"API Response: {json.dumps(data)}")

                if "webPages" not in data or "value" not in data["webPages"]:
                     return "No results found."

                web_pages = data["webPages"]["value"]

                if not web_pages:
                    return "No results found."

                formatted_results = []
                for r in web_pages:
                    title = r.get("name", "No Title")
                    url = r.get("url", "#")
                    snippet = r.get("snippet", "No snippet")
                    summary = r.get("summary", "")

                    entry = f"Title: {title}\nLink: {url}\nSnippet: {snippet}"
                    if summary:
                        entry += f"\nSummary: {summary[:200]}..."

                    formatted_results.append(entry)

                return "\n\n".join(formatted_results)

    except Exception as e:
        logger.error(f"Search failed: {e}")
        return f"Search failed: {str(e)}"
