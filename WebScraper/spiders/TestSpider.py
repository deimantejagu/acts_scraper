import scrapy

class TestSpider(scrapy.Spider):
    name = "TestSpider"

    start_urls = ["http://example.com"]

    async def go_to_acts(self, response):
        # Here we generate the request and yield it
        urls = ["http://example.com/page1", "http://example.com/page2"]
        print(f"Yielding request with URLs: {urls}")
        
        # Make sure that the correct meta data is being passed
        yield scrapy.Request(url=response.url, meta={'playwright': True, 'urls': urls}, callback=self.parse)

    def parse(self, response):
        print("In parse method")
        urls = response.meta.get('urls', [])
        print(f"URLs received in parse: {urls}")
        # You can follow all URLs here if needed
        yield from response.follow_all(urls[:5], meta={'playwright': True}, callback=self.parse_act)

    def parse_act(self, response):
        print("In parse_act")
        # Handle the final processing logic here
