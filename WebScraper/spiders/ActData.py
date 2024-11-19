import scrapy
import re

class ActdataSpider(scrapy.Spider):
    name = "ActData"
    allowed_domains = ["www.lrs.lt", "e-seimas.lrs.lt"]
    start_urls = ["https://www.lrs.lt/pls/inter/w5_show?p_k=2&p_r=4005"]

    def parse(self, response):
        # Extract URLs from the page
        urls = response.xpath("//tr/td[2]/a/@href").getall()

        valid_urls = [url for url in urls if url]

        yield from response.follow_all(valid_urls, self.parse_act)

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

        yield {
            "url": response.url,
            "title": title
        }
