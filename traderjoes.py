import asyncio
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

class Traderjoes():
    def __init__(self,url):
        self.url = url

    @logger
    async def get_prod_details(self,page):
        """
        Scrapes product details from multiple pages of a product listing.

        This method performs the following steps:
        1. Extracts the total number of pages from the pagination list. 
        2. Initializes lists to collect product details such as names, URLs, prices, categories, units, images, and IDs.
        3. Iterates through each page, scraping product information including:
        - Product names
        - Product URLs
        - Product prices
        - Product categories
        - Product units
        - Product image URLs
        - Product IDs
        4. Data cleaning and data extraction is done to the respective lists.
        5. Navigates to the next page and repeats the process until all pages are scraped.
        7. Returns a dictionary containing the collected product details.

        Args:
            page (pyppeteer.page.Page): The Pyppeteer page object used for interacting with the webpage.

        Returns:
            dict: A dictionary with lists of product details:
                - "product_names": List of product names
                - "product_urls": List of product URLs
                - "product_prices": List of product prices
                - "product_categories": List of product categories
                - "product_units": List of product units
                - "product_image_urls": List of lists of product image URLs
                - "Product_ids": List of product IDs
        """


        html_content = await utility.get_html_data(page=page,wait_selector='//ul[@class="Pagination_pagination__list__1JUIg"]')
        
        selector =  Selector(text=html_content)

        no_of_pages = selector.xpath('//ul[@class="Pagination_pagination__list__1JUIg"]/li[last()]/text()').get()
        try:
            ## UNCOMMENT THE BELOW LINE TO GET ALL DATA
            # no_of_pages=int(no_of_pages)
            no_of_pages = 3 #Comment this line
            logging.info(f"Total No of Pages {no_of_pages}")
        except:
            logger.error("Expected No of Pages is not an integer.")
            raise ValueError(no_of_pages)
        
        # Initializing lists to collect Product 
        list_of_product_name  = []
        list_of_product_url = []
        list_of_product_price =[]
        list_of_product_category=[]
        list_of_product_unit=[]
        list_of_product_image_urls=[]
        list_of_product_ids=[]
        
        logging.info("Initializing Scraping process....")
        # print("Products :\n")
        for page_no in range(1,no_of_pages):
            logging.info(f"Scraping page {page_no} started....")
            await page.waitFor('//ul[@class="Pagination_pagination__list__1JUIg"]') # Waiting for the element to load
            product_url = selector.xpath('//a[@class="Link_link__1AZfr ProductCard_card__img_link__2bBqA"]/@href').getall()
            id = [i.split('/')[-1] for i in product_url]
            product_url = [self.url+i for i in product_url] # Adding Base url
            product_name = selector.xpath('.//h2[@class="ProductCard_card__title__text__uiWLe"]/a/text()').getall()
            price = selector.xpath('.//span[@class="ProductPrice_productPrice__price__3-50j"]/text()').getall()
            category = selector.xpath('.//a[@class="Link_link__1AZfr ProductCard_card__category__Hh3rT"]/text()').getall()
            unit = selector.xpath('.//span[@class="ProductPrice_productPrice__unit__2jvkA"]/text()').getall()
            unit = [i.strip("/") for i in unit] # Removing "/" from Unit
            li_elements = selector.xpath('//ul[@class="ProductList_productList__list__3-dGs"]/li')
            image_url = []
            for index, li in enumerate(li_elements):
                srcset_urls = li.xpath('.//source/@srcset').getall()
                img_src_url = li.xpath('.//img/@src').getall()
                all_urls = srcset_urls + img_src_url
                image_url.append([self.url+i.strip() if i.strip().endswith(".webp") else self.url+i.strip()+".webp" for i in all_urls]) # Adding Base url and Extentions.

            
            if product_url:
                list_of_product_name.extend(product_name)
                list_of_product_url.extend(product_url)
                list_of_product_price.extend(price)
                list_of_product_unit.extend(unit)
                list_of_product_category.extend(category)
                list_of_product_image_urls.extend(image_url)
                list_of_product_ids.extend(id)
                # print("\n".join(product_name))
                logging.info(f"Scraping page {page_no} Completed....")
            else:
                logger.error("Expected Product url missing...")

            if page_no<no_of_pages:
                await page.goto(f"{product_base_url}?filters=%7B%22page%22%3A{page_no+1}%7D")
                await asyncio.sleep(5)
            else:
                break
        return {
            "product_names": list_of_product_name,
            "product_urls": list_of_product_url,
            "product_prices": list_of_product_price,
            "product_categories": list_of_product_category,
            "product_units": list_of_product_unit,
            "product_image_urls": list_of_product_image_urls,
            "Product_ids":list_of_product_ids
        }
        
    @logger
    def convert_to_custom_format(self,data):
        """
        Converts product data from a dictionary format to a custom JSON format.

        This method performs the following steps:
        1. Maps the keys in the input dictionary to new keys defined in `key_mapping`.
        2. Iterates through the list of product names and creates a new dictionary for each product.
        3. For each product, it assigns values from the input dictionary to the new keys according to the mapping.
        4. Collects all the product dictionaries into a list.
        5. Returns the list of product dictionaries in the custom format.

        Args:
            data (dict): A dictionary containing product data with keys such as 'product_names', 'product_urls', etc.

        Returns:
            list: A list of dictionaries, each representing a product with keys in the custom format.
        """

        key_mapping = {
            "Product_ids": "id",
            'product_names': 'title',
            'product_urls': 'url',
            'product_prices': 'price',
            'product_categories': 'category',
            'product_units': 'unit',
            'product_image_urls': 'image'
        }

        length = len(data['product_names'])
        result = []
        for i in range(length):
            product = {}
            for old_key, new_key in key_mapping.items():
                product[new_key] = data[old_key][i]
            result.append(product)

        return result

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

        global product_base_url
        product_base_url = f'{self.url}/home/products/category/products-2'
        await page.goto(product_base_url)
        logging.info('Sucessfull navigated to Products page...')   

        Product_dict = await self.get_prod_details(page)

        await browser.close()

        return Product_dict
    
    @logger
    def output(self,output_path):
        """
        Retrieves product data asynchronously, converts it to a custom JSON format, and saves it to a specified file.

        This method performs the following steps:
        1. Calls the asynchronous method `GetData()` to fetch product data.
        2. Converts the fetched data into a custom JSON format using `convert_to_custom_format()`.
        3. Saves the converted JSON data to a file at the path specified using `utility.output()`.

        """
        Product_dict = asyncio.get_event_loop().run_until_complete(self.GetData())
        json_data = self.convert_to_custom_format(Product_dict)

        return utility.output(json_data,output_path)



Traderjoes("https://www.traderjoes.com").output(output_path = "./output/traderjoes.json")