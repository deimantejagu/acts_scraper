import scrapy
import re
from datetime import date, datetime

class ActData(scrapy.Spider):
    name = "ActData"  
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
            
            print(f"urls: {urls}, skaicius: {len(urls)}")
        finally:
            await page.close()

        yield scrapy.Request(url=response.url, meta={'playwright': True, 'urls': urls}, callback=self.parse, dont_filter=True)

    async def extract_data(self, page):
        await page.wait_for_selector('xpath=//tbody[contains(@id, "resultsTable_data")]/tr/td[4]/a')
        links = page.locator('xpath=//tbody[@id="searchCompositeComponent:contentForm:resultsTable_data"]/tr/td[4]/a')

        # Extract all href attributes
        urls = []
        link_count = await links.count()
        for i in range(link_count):
            href = await links.nth(i).get_attribute('href')
            if href:
                urls.append(href)

        return urls

    def parse(self, response):
        # Retrieve the passed URLs
        urls = response.meta.get('urls', [])

        yield from response.follow_all(urls, meta={'playwright': True}, callback=self.parse_act)

    def parse_act(self, response):
        # Parsing act page

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
            "Date": date.today(),
            "title": title,
            "related_documents": related_documents,
            "file_urls": [docx_url]
        }
