import scrapy
import re
import time
from datetime import date
from WebScraper.items import ActDataItem

class ActData(scrapy.Spider):
    name = "ActData"  
    allowed_urls = ['e-seimas.lrs.lt']  
    start_urls = ["https://e-seimas.lrs.lt/portal/documentSearch/lt"]

    def start_requests(self):
        url = "https://e-seimas.lrs.lt/portal/documentSearch/lt"
        yield scrapy.Request(url, meta=dict(playwright=True, playwright_include_page=True), callback=self.go_to_acts_page)

    async def go_to_acts_page(self, response):
        page = response.meta["playwright_page"]
        all_links = []
        try:
            # Click todays date
            await page.locator('#searchCompositeComponent\\:contentForm\\:searchParamPane\\:j_id_30\\:adoptionDateInterval\\:paramAdoptionDateFrom\\:calendar_input').click()
            await page.locator('xpath=//a[contains(@class, "ui-state-highlight")]').click()
            await page.locator('xpath=//input[contains(@id, "searchCompositeComponent:contentForm:searchParamPane:j_id_30:adoptionDateInterval:j_id_3y:calendar_input")]').click()
            await page.locator('xpath=//a[contains(@class, "ui-state-highlight")]').click()

            # Click search button
            await page.locator('#searchCompositeComponent\\:contentForm\\:searchParamPane\\:searchButtonTop').click()

            while True:
                # Wait for the results table data to appear
                await page.wait_for_selector('tbody#searchCompositeComponent\\:contentForm\\:resultsTable_data')

                extracted_links = await self.extract_links(page)
                extracted_links = [response.urljoin(extracted_link) for extracted_link in extracted_links]
                all_links.extend(extracted_links)

                next_page_button = page.locator('.ui-paginator-bottom .ui-paginator-next:not(.ui-state-disabled)')
                if await next_page_button.is_visible():
                    await next_page_button.click()
                    time.sleep(5)
                else:
                    break
        finally:
            await page.close()
        yield scrapy.Request(url=response.url, meta={'playwright': True, 'all_links': all_links}, callback=self.parse, dont_filter=True)

    async def extract_links(self, page):
        await page.wait_for_selector('xpath=//tbody[contains(@id, "resultsTable_data")]/tr/td[4]/a')
        links = page.locator('xpath=//tbody[@id="searchCompositeComponent:contentForm:resultsTable_data"]/tr/td[4]/a')

        # Extract all links
        extracted_links = []
        links_count = await links.count()
        for i in range(links_count):
            href = await links.nth(i).get_attribute('href')
            extracted_links.append(href)

        return extracted_links

    def parse(self, response):
        # Retrieve the passed extracted_links
        all_links = response.meta.get('all_links', [])

        yield from response.follow_all(all_links, meta={'playwright': True}, callback=self.parse_act)

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

        actDataItem = ActDataItem()
        actDataItem['url'] = response.url
        actDataItem['date'] = date.today()
        actDataItem['title'] = title
        # atskira lentele???
        actDataItem['related_documents'] = related_documents
        actDataItem['file_urls'] = [docx_url]

        yield actDataItem
