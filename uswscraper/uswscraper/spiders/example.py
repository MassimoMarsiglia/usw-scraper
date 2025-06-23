import scrapy


class ExampleSpider(scrapy.Spider):
    name = "example"
    allowed_domains = ["httpbin.org"]
    start_urls = ["https://httpbin.org/ip"] * 10  # Simulating multiple requests
    

    def parse(self, response):
        # Log the proxy used for this request
        proxy_used = response.request.meta.get('proxy', 'No proxy')
        self.logger.info(f"Response from {response.url} using proxy: {proxy_used}")
        
        # Parse the JSON response to show the IP being used
        try:
            data = response.json()
            ip = data.get('origin', 'Unknown IP')
            self.logger.info(f"Current IP: {ip}")
            yield {'url': response.url, 'ip': ip, 'proxy': proxy_used}
        except:
            self.logger.error(f"Failed to parse JSON response from {response.url}")
