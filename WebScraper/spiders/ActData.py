import scrapy
import re
import os

class ActdataSpider(scrapy.Spider):
    name = "ActData"
    allowed_domains = ["www.lrs.lt", "e-seimas.lrs.lt"]
    start_urls = ["https://www.lrs.lt/pls/inter/w5_show?p_k=2&p_r=4005"]

    def parse(self, response):
        # Extract URLs from the page
        urls = response.xpath("//tr/td[2]/a/@href").getall()

        valid_urls = [url for url in urls if url]

        yield from response.follow_all(valid_urls[:5], self.parse_act)

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
        
        # Extract document
        docx_url = response.xpath("//div[contains(@class, 'ui-widget-header') and contains(@class, 'ui-corner-top') and contains(@class, 'pe-layout-pane-header') and contains(@class, 'centerHeader')]//a[@href]/@href").get()
        docx_url = response.urljoin(docx_url)

        # Extract related documents
        related_documents = response.xpath("//div[@id='mainForm:accordionRight:j_id_b0:0:j_id_b1_content']//a[@href]/@href").getall()
        # related_documents = [response.urljoin(doc) for doc in related_documents]

        yield {
            "url": response.url,
            "Date": date,
            "title": title,
            "related_documents": related_documents,
            # "file_urls": [docx_url]
        }
