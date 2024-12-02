import scrapy
import re
import time
from datetime import date, datetime
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
            await page.locator('#searchCompositeComponent\\:contentForm\\:searchParamPane\\:searchButtonTop').click()
            print("Button is clicked")

            while True:
                # Wait for the results table data to appear
                await page.wait_for_selector('tbody#searchCompositeComponent\\:contentForm\\:resultsTable_data')

                extracted_links = await self.extract_valid_acts_links(page)
                extracted_links = [response.urljoin(extracted_link) for extracted_link in extracted_links]
                print(f"extracted_links: {extracted_links}, skaicius: {len(extracted_links)}")

                if len(extracted_links) <= 0 or len(all_links ) >= 21:
                    break
                
                all_links.extend(extracted_links)
                print(f"all_links: {len(all_links)}")

                # css selector: .ui-paginator-bottom .ui-paginator-next:not(.ui-state-disabled)

                print('attempting to go to next page')
                await page.locator('.ui-paginator-bottom .ui-paginator-next:not(.ui-state-disabled)').click()
                time.sleep(5)
        finally:
            await page.close()
        print("visi_linkai")
        for i, link in enumerate(all_links):
            print(f"{i} {link}")
        yield scrapy.Request(url=response.url, meta={'playwright': True, 'all_links': all_links}, callback=self.parse, dont_filter=True)

    async def extract_valid_acts_links(self, page):
        await page.wait_for_selector('xpath=//tbody[contains(@id, "resultsTable_data")]/tr/td[6]/span')
        dates = page.locator('xpath=//tbody[@id="searchCompositeComponent:contentForm:resultsTable_data"]/tr/td[6]/span')

        await page.wait_for_selector('xpath=//tbody[contains(@id, "resultsTable_data")]/tr/td[4]/a')
        links = page.locator('xpath=//tbody[@id="searchCompositeComponent:contentForm:resultsTable_data"]/tr/td[4]/a')

        # Extract all links
        extracted_links = []
        dates_count = await dates.count()
        for i in range(dates_count):
            print(f"iteratorius: {i}")
            extracted_date = datetime.strptime(await dates.nth(i).text_content(), "%Y-%m-%d")
            if extracted_date.date() == date.today():
                href = await links.nth(i).get_attribute('href')
                print(f"href: {href}")
                extracted_links.append(href)

        return extracted_links

    def parse(self, response):
        # Retrieve the passed extracted_links
        all_links = response.meta.get('all_links', [])
        print(f"visiii {len(all_links)}")

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
        actDataItem['related_documents'] = related_documents
        actDataItem['file_urls'] = [docx_url]

        yield actDataItem
