from core.tools import registry
from duckduckgo_search import DDGS
import logging

logger = logging.getLogger(__name__)

@registry.register(name="web_search", description="Search the web for information using DuckDuckGo.")
async def web_search(query: str, max_results: int = 5):
    """
    Perform a web search.

    Args:
        query: The search query string.
        max_results: Maximum number of results to return (default 5).
    """
    logger.info(f"Searching web for: {query}")
    try:
        # DDGS context manager is synchronous in some versions, but library supports async?
        # The latest duckduckgo_search might be synchronous or async.
        # Let's check if DDGS() works as context manager.
        # It seems `ddgs.text()` is synchronous in the standard usage.
        # Since we are in async function, we should ideally run this in executor if it blocks,
        # but for simplicity and low overhead, we'll try running it directly.
        # If it blocks too much, we might need run_in_executor.

        results = []
        with DDGS() as ddgs:
            # list() iterates the generator. Use backend="html" for stability.
            for r in ddgs.text(query, max_results=max_results, backend="html"):
                results.append(r)

        if not results:
            # Fallback to lite backend if html fails or returns empty
            try:
                with DDGS() as ddgs:
                    for r in ddgs.text(query, max_results=max_results, backend="lite"):
                        results.append(r)
            except Exception:
                pass

        if not results:
            return "No results found."

        formatted_results = []
        for r in results:
            formatted_results.append(f"Title: {r.get('title')}\nLink: {r.get('href')}\nSnippet: {r.get('body')}")

        return "\n\n".join(formatted_results)
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return f"Search failed: {str(e)}"
