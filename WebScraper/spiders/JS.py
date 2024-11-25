import scrapy

class JS(scrapy.Spider):
    name = "JS"
    
    def start_requests(self):
        url = "https://e-seimas.lrs.lt/portal/legalAct/lt/TAK/82027d66aaf711efaae6a4c601761171?positionInSearchResults=11&searchModelUUID=23d4ceba-3192-419d-9096-b583160524ef"
        yield scrapy.Request(url, meta={'playwright': True}, callback=self.parse)

    def parse(self, response):
        # Use Playwright to render and get the required date
        related_documents = response.xpath("//div[@id='mainForm:accordionRight:j_id_b0:0:j_id_b1_content']//a[@href]/@href").getall()
        related_documents = [response.urljoin(doc) for doc in related_documents]
        yield {'related_documents': related_documents}



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