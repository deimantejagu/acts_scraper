import scrapy
import re

class JS(scrapy.Spider):
    name = "JS"  
    allowed_urls = ['e-seimas.lrs.lt']  
    start_urls = ["https://e-seimas.lrs.lt/portal/documentSearch/lt"]

    def start_requests(self):
        url = "https://e-seimas.lrs.lt/portal/documentSearch/lt"
        yield scrapy.Request(url, meta=dict(playwright=True, playwright_include_page=True), callback=self.go_to_acts)

    async def go_to_acts(self, response):
        page = response.meta["playwright_page"]
        try:
            await page.locator('#searchCompositeComponent\\:contentForm\\:searchParamPane\\:searchButtonTop').click()
            await page.wait_for_selector('tbody#searchCompositeComponent\\:contentForm\\:resultsTable_data')

            urls = await self.extract_data(page)
            urls = [response.urljoin(url) for url in urls]
            
            print(f"urls: {urls}")
        finally:
            await page.close()

        yield scrapy.Request(url=response.url, meta={'playwright': True, 'urls': urls}, callback=self.parse, dont_filter=True)

    async def extract_data(self, page):
        links = page.locator('xpath=//tbody[@id="searchCompositeComponent:contentForm:resultsTable_data"]/tr/td[4]/a')

        # Extract all href attributes
        urls = []
        link_count = await links.count()
        for i in range(link_count):
            href = await links.nth(i).get_attribute('href')
            if href:
                urls.append(href)

        print("Extracted URLs:", urls)
                
        return urls

    def parse(self, response):
        print("labas")
        # Retrieve the passed URLs
        urls = response.meta.get('urls', [])
        print(f"URLs received in parse: {urls}")

        # Follow the first 5 URLs
        yield from response.follow_all(urls[:5], meta={'playwright': True}, callback=self.parse_act)

    def parse_act(self, response):
        # Parsing redirected page

        # Extract date
        date = response.xpath("//tr[contains(@class, 'ui-widget-content') and contains(@class, 'ui-panelgrid-even')]//td[8]/text()").get()

        # Extract title
        pattern = r'[„"](.*?)[“"]'
        raw_title = response.xpath("//span[@id='mainForm:laTitle']/text()").get()
        if raw_title:
            match = re.search(pattern, raw_title)
            if match:
                title = match.group(1) 
            else: 
                title = raw_title
        else:
            title = None

        # Extract related documents
        related_documents = response.xpath("//div[@id='mainForm:accordionRight:j_id_b0:0:j_id_b1_content']//a[@href]/@href").getall()
        related_documents = [response.urljoin(doc) for doc in related_documents]
        
        # Extract document
        docx_url = response.xpath("//div[contains(@class, 'ui-widget-header') and contains(@class, 'ui-corner-top') and contains(@class, 'pe-layout-pane-header') and contains(@class, 'centerHeader')]//a[@href]/@href").get()
        docx_url = response.urljoin(docx_url)

        yield {
            "url": response.url,
            "Date": date,
            "title": title,
            "related_documents": related_documents,
            "file_urls": [docx_url]
        }


# import scrapy

# class JS(scrapy.Spider):
#     name = "JS"
    
#     def start_requests(self):
#         url = "https://e-seimas.lrs.lt/portal/legalAct/lt/TAK/82027d66aaf711efaae6a4c601761171?positionInSearchResults=11&searchModelUUID=23d4ceba-3192-419d-9096-b583160524ef"
#         yield scrapy.Request(url, meta={'playwright': True}, callback=self.parse)

#     def parse(self, response):
#         # Use Playwright to render and get the required date
#         related_documents = response.xpath("//div[@id='mainForm:accordionRight:j_id_b0:0:j_id_b1_content']//a[@href]/@href").getall()
#         related_documents = [response.urljoin(doc) for doc in related_documents]
#         yield {'related_documents': related_documents}



# import scrapy

# from WebScraper.items import QuoteItem

# class JS(scrapy.Spider):
#     name = "JS"
#     # allowed_domains = ["quotes.toscrape.com"]
#     # start_urls = ["https://quotes.toscrape.com/js/"]

#     def start_requests(self):
#         url = "https://quotes.toscrape.com/js/"

#         yield scrapy.Request(url, meta={'playwright': True})

#     def parse(self, response):
#         for quote in response.xpath("//div[@class='quote']"):
#             quote_item = QuoteItem()
#             quote_item['text'] = quote.xpath("//span[@class='text']/text()").get()
#             quote_item['author'] = quote.xpath(".//span/small[@class='author']/text()").get()
#             quote_item['tags'] = quote.xpath(".//div[@class='tags']//a[@class='tag']/text()").getall()

#             yield quote_item