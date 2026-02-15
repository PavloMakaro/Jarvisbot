from core.tools import registry
import aiohttp
import config
import logging
import os
import io

logger = logging.getLogger(__name__)

@registry.register(name="ocr_image", description="Extract text from an image URL or file path using OCR.")
async def ocr_image(image_url: str = None, file_path: str = None, language: str = "eng"):
    """
    Extract text from an image.

    Args:
        image_url: The URL of the image to process.
        file_path: The local path of the image to process.
        language: The language code (e.g., 'eng', 'rus'). Default 'eng'.
    """
    if not image_url and not file_path:
        return "Please provide either an image URL or a file path."

    api_url = "https://api.ocr.space/parse/image"

    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; GarvisBot/1.0; +http://example.com/bot)"}
        async with aiohttp.ClientSession(headers=headers) as session:
            file_obj = None
            filename = "image.jpg"
            should_close_file = False

            # Download image if URL provided
            if image_url:
                try:
                    async with session.get(image_url) as resp:
                        if resp.status != 200:
                            return f"Failed to download image from URL. Status: {resp.status}"
                        file_bytes = await resp.read()
                        file_obj = io.BytesIO(file_bytes)

                        # Try to infer filename
                        path = image_url.split("?")[0]
                        if os.path.splitext(path)[1]:
                            filename = os.path.basename(path)
                except Exception as e:
                    return f"Failed to download image: {e}"

            elif file_path:
                if not os.path.exists(file_path):
                    return f"File not found: {file_path}"
                file_obj = open(file_path, "rb")
                filename = os.path.basename(file_path)
                should_close_file = True

            # Prepare OCR request
            data = aiohttp.FormData()
            data.add_field("apikey", config.OCR_API_KEY)
            data.add_field("language", language)
            data.add_field("OCREngine", "2")
            data.add_field("isOverlayRequired", "false")

            if file_obj:
                data.add_field("file", file_obj, filename=filename)

            try:
                async with session.post(api_url, data=data) as response:
                    if response.status != 200:
                         return f"OCR API returned status {response.status}: {await response.text()}"

                    try:
                        result = await response.json()
                    except Exception:
                        return f"Failed to parse OCR response: {await response.text()}"

                    if isinstance(result, str):
                        return f"OCR Error: {result}"

                    if result.get("IsErroredOnProcessing"):
                        error_msg = result.get("ErrorMessage")
                        if isinstance(error_msg, list):
                            error_msg = ", ".join(error_msg)
                        return f"OCR Error: {error_msg}"

                    parsed_results = result.get("ParsedResults")
                    if not parsed_results:
                        return "No text found."

                    text = parsed_results[0].get("ParsedText")
                    return text if text else "No text could be extracted."

            finally:
                if should_close_file and file_obj:
                    file_obj.close()

    except Exception as e:
        logger.error(f"OCR failed: {e}")
        return f"OCR failed: {str(e)}"
