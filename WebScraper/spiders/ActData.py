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

            extracted_links = await self.extract_data(page)
            extracted_links = [response.urljoin(extracted_link) for extracted_link in extracted_links]
            
            print(f"extracted_links: {extracted_links}, skaicius: {len(extracted_links)}")
        finally:
            await page.close()

        yield scrapy.Request(url=response.url, meta={'playwright': True, 'extracted_links': extracted_links}, callback=self.parse, dont_filter=True)

    async def extract_data(self, page):
        await page.wait_for_selector('xpath=//tbody[contains(@id, "resultsTable_data")]/tr/td[6]/span')
        dates = page.locator('xpath=//tbody[@id="searchCompositeComponent:contentForm:resultsTable_data"]/tr/td[6]/span')

        await page.wait_for_selector('xpath=//tbody[contains(@id, "resultsTable_data")]/tr/td[4]/a')
        links = page.locator('xpath=//tbody[@id="searchCompositeComponent:contentForm:resultsTable_data"]/tr/td[4]/a')

        # Extract all links
        extracted_links = []
        dates_count = await dates.count()
        for i in range(dates_count):
            print(f"iteratorius: {i}")
            extracted_date = await dates.nth(i).text_content()
            extracted_date = datetime.strptime(extracted_date, "%Y-%m-%d")
            print(f"extracted_date: {extracted_date}")
            if extracted_date.date() == date.today():
                print(f"extracted_date.date(): {extracted_date.date()}")
                href = await links.nth(i).get_attribute('href')
                print(f"href: {href}")
                extracted_links.append(href)


        return extracted_links

    def parse(self, response):
        # Retrieve the passed extracted_links
        extracted_links = response.meta.get('extracted_links', [])

        yield from response.follow_all(extracted_links, meta={'playwright': True}, callback=self.parse_act)

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
            # "Date": date.today(),
            "title": title,
            # "related_documents": related_documents,
            # "file_urls": [docx_url]
        }
