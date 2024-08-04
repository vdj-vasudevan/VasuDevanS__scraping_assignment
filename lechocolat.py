import asyncio
import os
import json
import logging
from parsel import Selector
from functools import wraps
import utility 


def logger(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        log = logging.getLogger(fn.__name__)
        log.info('About to run %s' % fn.__name__)
        out = fn(*args, **kwargs)
        log.info('Done running %s' % fn.__name__)
        return out
    return wrapper

FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LEVEL = logging.INFO
logging.basicConfig(format=FORMAT, level=LEVEL)
log = logging.getLogger(__name__)
log.info('Entered module: %s' % __name__)

class Lechocolat():
    def __init__(self,url):
        self.url = url

    @logger
    async def get_prod_details(self,page):
        try:
            html_content = await utility.get_html_data(page=page,wait_selector='//h1[@class="headerLogo__image"]')
            selector =  Selector(text=html_content)
            Product_data_list=[]
            
            return Product_data_list
        except Exception as err:
            raise err

    @logger
    async def GetData(self):
        """
        Asynchronously retrieves product details from a specified category page using a headless browser.

        This method performs the following steps:
        1. Launches a headless browser and opens a new page.
        2. Navigates to the product category page using the `base_url` attribute.
        3. Calls `self.get_prod_details(page)` to fetch product details from all the pages.
        4. Closes the browser.
        5. Returns the product details as a dictionary.

        Returns:
            dict: A dictionary containing product details retrieved from the page.
        """
        browser = await utility.get_browser()
        page = await browser.newPage()
        await page.goto(self.url)
        logging.info('Sucessfull navigated to Products page...')   
        
        Product_data_list = await self.get_prod_details(page)

        await browser.close()

        return Product_data_list
    
    
    @logger
    def output(self,output_path):
        """
        Retrieves product data asynchronously, converts it to a custom JSON format, and saves it to a specified file.

        This method performs the following steps:
        1. Calls the asynchronous method `GetData()` to fetch product data.
        2. Converts the fetched data into a custom JSON format using `convert_to_custom_format()`.
        3. Saves the converted JSON data to a file at the path specified using `utility.output()`.

        """
        json_data = asyncio.get_event_loop().run_until_complete(self.GetData())

        return utility.output(json_data,output_path)


Lechocolat("https://www.lechocolat-alainducasse.com/uk/").output(output_path = "./output/lechocolat.json")

### Note not able to replicate discount part Unlock 20% off your first order.

## error faced is 404 Page Not Found
## The page you requested does not exist.  