

import scrapy
from news.items import NewsItem

class ToiSpider(scrapy.Spider):
    name = "toi"

    # Define URLs and corresponding XPaths
    categories = {
        "world": "https://timesofindia.indiatimes.com/world",
        "india": "https://timesofindia.indiatimes.com/india",
        "business": "https://timesofindia.indiatimes.com/business",
        "technology": "https://timesofindia.indiatimes.com/technology",
    }

    xpaths = {
        "world": '//div[@class="lM9xY "]//div[@class="iN5CR"]//a/@href',
        "india": '//div[@class="lM9xY "]//div[@class="iN5CR"]//a/@href',
        "business": '//div[@class="wRxdF   undefined"]//a/@href',
        "technology": '//div[@class="wRxdF top-section speakinglandingpage  undefined"]//a/@href',
    }

    def start_requests(self):
        for category, url in self.categories.items():
            yield scrapy.Request(url=url, callback=self.parse, meta={"category": category})

    def parse(self, response):
        category = response.meta.get("category")
        xpath = self.xpaths.get(category)
        if not xpath:
            self.logger.warning(f"No XPath found for category: {category}")
            return

        links = response.xpath(xpath).getall()
        self.logger.info(f"Found {len(links)} links for category: {category}")

        for link in links[:5]:  # Limit to 5 links
            yield scrapy.Request(
                url=link,
                callback=self.parse_article,
                meta={"category": category}
            )

    def parse_article(self, response):
        title = response.xpath('//h1[@class="HNMDR"]/span/text()').get()
        paragraphs = response.xpath('//div[@class="_s30J clearfix  "]/text()').getall()
        body_text = " ".join(paragraphs)

        news_item = NewsItem()
        news_item['category'] = response.meta.get('category', 'unknown')
        news_item['title'] = title
        news_item['body_text'] = body_text

        yield news_item

# response.xpath('//div[@class="lM9xY "]//div[@class="iN5CR"]//a/@href').getall()
# response.xpath('//div[@class="wRxdF   undefined"]//a/@href').getall()  # business links
# response.xpath('//div[@class="wRxdF top-section speakinglandingpage  undefined"]//a/@href').getall() # tech links
## response.xpath('//div[@class="atWBy Q6d5H grid_wrapper"]//div[@class="col_l_6"]//figure//a/@href').getall()
# response.xpath('//div[@class="_s30J clearfix  "]/text()').getall()  # body
# response.xpath('//h1[@class="HNMDR"]/span/text()').getall()  # title


