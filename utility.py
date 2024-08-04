import json
import asyncio
import pyppeteer

def save_json_data(data,file_path):
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    return

async def get_browser():
    return await pyppeteer.launch(
            {"args": 
             [
                "--incognito",
                "--ignore-certificate-errors",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--window-size=1920,1080",
                "--disable-accelerated-2d-canvas",
                "--disable-gpu",
                "--disable-infobars"
            ],
            "defaultViewport": None,
            "headless": True,
            "ignoreHTTPSErrors": True,})

async def get_html_data(page,wait_selector):
    """
    Waits for a specific element to load on the page and returns the page's HTML content.

    This function performs the following steps:
    1. Waits for the specified selector to be present on the page.
    2. Extracts the HTML content of the entire page.

    Args:
        page (pyppeteer.page.Page): The Pyppeteer page object used for interacting with the webpage.
        wait_selector (str): The CSS or XPath selector to wait for before extracting the HTML content.

    Returns:
        str: The HTML content of the page as a string.
    """
    await page.waitFor(wait_selector)
    html_content = await page.evaluate('document.body.innerHTML')
    return html_content

async def get_full_html_data(page,wait_selector):
    """
    Waits for a specific element to load on the page and returns the page's HTML content.

    This function performs the following steps:
    1. Waits for the specified selector to be present on the page.
    2. Extracts the HTML content of the entire page.

    Args:
        page (pyppeteer.page.Page): The Pyppeteer page object used for interacting with the webpage.
        wait_selector (str): The CSS or XPath selector to wait for before extracting the HTML content.

    Returns:
        str: The HTML content of the page as a string.
    """
    await page.waitFor(wait_selector)
    html_content = await page.evaluate('document.documentElement.outerHTML')
    return html_content

def output(json_data,output_path = "./output/traderjoes.json"):
        """
        saves it to a specified file.

        This method performs the following steps:
        1. Saves the converted JSON data to a file at the path specified using `save_data()`.

        """

        save_json_data(json_data,output_path)
