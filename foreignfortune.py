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

class Foreignfortune():
    def __init__(self,url):
        self.url = url

    @logger
    async def get_prod_details(self,page):
        """
        Asynchronously retrieves product details from a series of categories on a website.

        This method navigates through a list of categories and their respective pages, extracts product URLs, 
        and collects detailed information for each product.

        Args:
            page (puppeteer.Page): The Puppeteer page object used for interacting with the web pages.

        Returns:
            list: A list of dictionaries, each containing product details extracted from the website.

        Raises:
            Exception: If there are issues with navigating pages or extracting data.

        Notes:
            - The method assumes that the page structure and XPaths are consistent with those specified in the code.
            - It uses environment variables to fetch the XPath for product details.
        """
        try:
            html_content = await utility.get_html_data(page=page,wait_selector='//ul[@class="site-nav list--inline site-nav--centered"]')
            selector =  Selector(text=html_content)
            list_of_category = selector.xpath('//ul[@class="site-nav list--inline site-nav--centered"]/li/a/text()').getall()
            list_of_category_urls = selector.xpath('//ul[@class="site-nav list--inline site-nav--centered"]/li/a/@href').getall()

            Product_data_list = []
            category_urls = {k:self.url + v for k,v in zip(list_of_category,list_of_category_urls)}

            ffHeaderXpath = '//h1[@class="collection-hero__title page-width"]'
            for category,url in category_urls.items():
                await page.goto(url=url)
                category_html_data = await utility.get_html_data(page=page,wait_selector=ffHeaderXpath)
                selector =  Selector(text=category_html_data)
                check_pagination = selector.xpath(os.environ['ffPaginationXpath']).getall()
                check_pagination = ["page1"] if not check_pagination else ["page1"]+check_pagination
                for page_ in check_pagination:
                    if page_ != "page1":
                        await page.goto(url= self.url + page_)
                        html_content = await utility.get_html_data(page=page,wait_selector=ffHeaderXpath)
                        selector =  Selector(text=html_content)

                        
                    product_url_list = selector.xpath('//div[@class="grid-view-item product-card"]/a/@href').getall()
                    for pr_url in product_url_list:
                        await page.goto(url=self.url+pr_url)
                        html_content = await utility.get_full_html_data(page=page,wait_selector='//h1[@class="product-single__title"]')
                        selector =  Selector(text=html_content)
                        Product_details = selector.xpath(os.environ["ffProductDetailsXpath"]).get()
                        prod_data = json.loads(Product_details)
                        Product_data_list.append(prod_data)

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


Foreignfortune("https://foreignfortune.com").output(output_path = "./output/foreignfortune.json")

### Note not able to replicate discount part Unlock 20% off your first order.

## error faced is 404 Page Not Found
## The page you requested does not exist.  