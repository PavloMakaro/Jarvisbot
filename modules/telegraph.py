import aiohttp
import json
import logging
from core.tools import registry
import os

logger = logging.getLogger(__name__)

API_ROOT = "https://api.telegra.ph"

class TelegraphClient:
    def __init__(self):
        self.access_token = None
        self.short_name = "GarvisBot"
        self.author_name = "Garvis Bot"

    async def create_account(self):
        """Creates a Telegraph account or reuses existing token if saved."""
        url = f"{API_ROOT}/createAccount"
        params = {
            "short_name": self.short_name,
            "author_name": self.author_name
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    data = await response.json()
                    if data.get("ok"):
                        self.access_token = data["result"]["access_token"]
                        return self.access_token
                    else:
                        logger.error(f"Failed to create Telegraph account: {data.get('error')}")
                        return None
        except Exception as e:
            logger.error(f"Error creating Telegraph account: {e}")
            return None

    def _convert_text_to_content(self, text):
        nodes = []
        lines = text.split("\n")

        current_list = None

        for line in lines:
            line = line.strip()
            if not line:
                if current_list:
                    nodes.append(current_list)
                    current_list = None
                continue

            if line.startswith("# "):
                if current_list:
                    nodes.append(current_list)
                    current_list = None
                nodes.append({"tag": "h3", "children": [line[2:]]})

            elif line.startswith("## "):
                if current_list:
                    nodes.append(current_list)
                    current_list = None
                nodes.append({"tag": "h4", "children": [line[3:]]})

            elif line.startswith("- ") or line.startswith("* "):
                if not current_list:
                    current_list = {"tag": "ul", "children": []}
                current_list["children"].append({"tag": "li", "children": [line[2:]]})

            else:
                if current_list:
                    nodes.append(current_list)
                    current_list = None
                nodes.append({"tag": "p", "children": [line]})

        if current_list:
            nodes.append(current_list)

        return json.dumps(nodes)

    async def create_page(self, title, content_text):
        if not self.access_token:
            if not await self.create_account():
                return "Failed to authenticate with Telegraph."

        url = f"{API_ROOT}/createPage"

        content_json = self._convert_text_to_content(content_text)

        data = {
            "access_token": self.access_token,
            "title": title,
            "author_name": self.author_name,
            "content": content_json,
            "return_content": "false"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=data) as response:
                    result = await response.json()
                    if result.get("ok"):
                        return result["result"]["url"]
                    else:
                        return f"Failed to create page: {result.get('error')}"
        except Exception as e:
            return f"Error creating page: {e}"

client = TelegraphClient()

@registry.register(name="create_telegraph_page", description="Create a Telegraph page (article).")
async def create_telegraph_page(title: str, content: str):
    """
    Create a Telegraph page.

    Args:
        title: The title of the article.
        content: The text content of the article. Supports basic Markdown (#, ##, -, *).
    """
    # Create the page
    url = await client.create_page(title, content)
    return url
