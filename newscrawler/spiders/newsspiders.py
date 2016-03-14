import scrapy
from scrapy.spiders import XMLFeedSpider

class BBCSpider(XMLFeedSpider):
    name = 'bbc'
    start_urls = [
        "http://feeds.bbci.co.uk/news/rss.xml"
    ]

    def parse(self, response):
        for item in response.selector.xpath('//item'):
            print(item.xpath('./title/text()').extract())
