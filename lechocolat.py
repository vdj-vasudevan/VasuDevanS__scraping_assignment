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
        """
        Scrapes product details from a website.

        This method navigates through category and product pages to collect detailed information about each product. It extracts various attributes such as product ID, image URL, title, category, description, price, weight, and the URL of the product page.

        Args:
            page (pyppeteer.page.Page): The Pyppeteer page object used for navigation and scraping.

        Returns:
            list[dict]: A list of dictionaries where each dictionary contains details of a single product.

        Raises:
            Exception: If an error occurs during the scraping process, it raises the exception.
        """
        try:
            html_content = await utility.get_html_data(page=page,wait_selector='//h1[@class="headerLogo__image"]')
            selector =  Selector(text=html_content)
            Product_data_list=[]
            category_urls = selector.xpath('//li[@class="siteMenuItem" and @data-depth="2"]/a/@href').getall()
            for cat_url in category_urls:
                print(f"Navigating to {cat_url}")
                await page.goto(cat_url)
                html_content = await utility.get_html_data(page=page,wait_selector='//section[@class="productMiniature__data"]')
                selector =  Selector(text=html_content)
                each_prod_url = selector.xpath('//section[@class="productMiniature__data"]/a/@href').getall()
                for n,each_prod in enumerate(each_prod_url):
                    # if n==2:
                        # break
                    print(f"Navigating to {each_prod}")
                    try:
                        product_unit= {}
                        await page.goto(each_prod)
                        html_content = await utility.get_html_data(page=page)
                        selector = Selector(text=html_content)
                        product_unit["id"] = each_prod.split("/")[-1]
                        product_unit['image_url'] = selector.xpath('//li[@class="productImages__item keen-slider__slide"]/a/@href').get()
                        product_unit["title"] = selector.xpath('//h1[@class="productCard__title"]/text()').get()
                        product_unit["categoty"] = selector.xpath('//h2[@class="productCard__subtitle"]/text()').get()
                        description = selector.css('div.productAccordion__content > p::text').getall()
                        product_unit["description"] = " ".join([desc.strip() for desc in description])
                        product_unit["price"] = selector.css('div.productAccordion__content > p::text').re_first(r'£\d+\.\d+')
                        product_unit["weight"] = selector.xpath('//p[@class="productCard__weight"]/text()').get()
                        product_unit['url'] = each_prod
                        Product_data_list.append(product_unit)
                        await asyncio.sleep(1)
                    except Exception as err:
                        id = each_prod.split("/")[-1]
                        logger.error(f"Error occuered while fetching {id} error : {err}...")
                        await asyncio.sleep(5) 

            return Product_data_list
        except Exception as err:
            logger.error(f"Error occuered : {err}...")
            return Product_data_list

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