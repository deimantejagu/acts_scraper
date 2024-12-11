import scrapy
import asyncio
from datetime import date
import time

class Test(scrapy.Spider):
    name = "Test"

    def start_requests(self):
        # Replace with your single test link
        test_url = "https://e-seimas.lrs.lt/portal/legalAct/lt/TAK/be792b24b5fd11efbb3fe9794b4a33e2?positionInSearchResults=11&searchModelUUID=a925f878-5ac5-4b3b-abd1-169bd44e663c"
        yield scrapy.Request(test_url, meta=dict(playwright=True, playwright_include_page=True), callback=self.parse_act)

    async def parse_act(self, response):
        page = response.meta.get("playwright_page", None)
        related_documents = []
        await page.wait_for_selector('xpath=//div[contains(@class, "ui-layout-content pe-layout-pane-content eastContent")]/div[contains(@id, "mainForm:accordionRight")]')
        open_tab = page.locator('xpath=//div[contains(@class, "ui-layout-content pe-layout-pane-content eastContent")]/div[contains(@id, "mainForm:accordionRight")]')
        if await open_tab.is_visible():
            await open_tab.click()

            await asyncio.sleep(3)
            while True:
                await page.wait_for_selector('xpath=//div[@id="mainForm:accordionRight:j_id_b0:0:j_id_b1_content"]')

                related_documents_links = response.xpath("//div[@id='mainForm:accordionRight:j_id_b0:0:j_id_b1_content']//a[@href]/@href").getall()
                related_documents_links = [response.urljoin(doc) for doc in related_documents_links]
                related_documents.extend(related_documents_links)
                print(f"related12: {len(related_documents)}")
                for doc in related_documents:
                    print(doc)

                await page.wait_for_selector('xpath=//div[contains(@id, "mainForm:accordionRight:j_id_b0:0:j_id_b1_paginator_top")]/span[contains(@class, "ui-paginator-next")]')
                next_page_button = page.locator('xpath=//div[contains(@id, "mainForm:accordionRight:j_id_b0:0:j_id_b1_paginator_top")]/span[contains(@class, "ui-paginator-next")]')
                if await next_page_button.is_visible() and await next_page_button.is_enabled():
                    await next_page_button.click()
                    await asyncio.sleep(5)
                else:
                    break
        else:
            print("Nematomas")
