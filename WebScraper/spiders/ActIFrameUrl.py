import scrapy

class ActIFrameUrl(scrapy.Spider):
    name = "ActIFrameUrl"
    allowed_domains = ["www.lrs.lt", "e-seimas.lrs.lt"]
    start_urls = ["https://www.lrs.lt/pls/inter/w5_show?p_k=2&p_r=4005"]

    def parse(self, response):
        # Extract URLs from the page
        urls = response.xpath("//tr/td[2]/a/@href").getall()

        valid_urls = [url for url in urls if url]

        yield from response.follow_all(valid_urls, self.parse_act)

    def parse_act(self, response):
        iframe_url = response.xpath("//iframe[@id='legalActResourceURLIframe']/@src").get()
        
        yield response.follow(response.urljoin(iframe_url), self.parse_iframe, meta={'parent_url': response.url})

    def parse_iframe(self, response):

        yield {
            "url": response.url,
        }
