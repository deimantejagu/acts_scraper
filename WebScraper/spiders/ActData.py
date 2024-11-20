import scrapy
import re
import requests

class ActdataSpider(scrapy.Spider):
    name = "ActData"
    allowed_domains = ["www.lrs.lt", "e-seimas.lrs.lt"]
    start_urls = ["https://www.lrs.lt/pls/inter/w5_show?p_k=2&p_r=4005"]

    def parse(self, response):
        # Extract URLs from the page
        urls = response.xpath("//tr/td[2]/a/@href").getall()

        valid_urls = [url for url in urls if url]

        yield from response.follow_all(valid_urls[:2], self.parse_act)

    def parse_act(self, response):
        # Parsing redirected page
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

        docx_url = response.xpath("//div[contains(@class, 'ui-widget-header') and contains(@class, 'ui-corner-top') and contains(@class, 'pe-layout-pane-header') and contains(@class, 'centerHeader')]//a[@href]/@href").get()
        docx_url = response.urljoin(docx_url)

        yield {
            "url": response.url,
            "title": title,
            "file_urls": [docx_url]
        }
