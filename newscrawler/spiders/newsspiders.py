import gzip
import datetime
import pymongo
import yaml
from email.utils import parsedate_to_datetime
import pymongo.errors

import scrapy
from scrapy.spiders import XMLFeedSpider
from newscrawler.items import NewsItem

TZ_UTC = datetime.timezone.utc
config = yaml.load(open('./config.yml', 'rb'))
sources = config['sources']

# Get and initialize mongo db
mongo_db = pymongo.MongoClient()[config['mongo_db_name']]
mongo_db.news.create_index('url', unique=True)

def aware_utc_now():
    return datetime.datetime.now(TZ_UTC)

class _MySpider(XMLFeedSpider):
    """ This is supposed to be used as the base class of other spider class.
    
    This class will set the `start_urls` automatically according to "./config.yml".
    """
    def __init__(self, *args, **kwargs):
        self.start_urls = sources[self.name]
        super().__init__(*args, **kwargs)

class SimpleGeneralSpider(_MySpider):
    """ This spider download and parse news rss and yield a :class:`NewsItem`
    for each news item. Note that this class is supposed to be used for
    debugging and normally, spiders such as :class:`GeneralSpider` should be
    used. """

    name = 'simple_general'

    def parse(self, response):
        now = aware_utc_now()
        for item in response.selector.xpath('//item'):
            news_item = NewsItem()
            news_item['url'] = item.xpath('./link/text()').extract()[0]
            news_item['title'] = item.xpath('./title/text()').extract()[0]
            news_item['description'] = item.xpath('./description/text()').extract()[0]
            # Make sure the publish date is in UTC.
            news_item['pub_date'] = parsedate_to_datetime(item.xpath('./pubDate/text()').extract()[0]).astimezone(TZ_UTC)
            news_item['crawl_time'] = now
            yield news_item


class GeneralSpider(SimpleGeneralSpider):
    """ Downloads, parses and stores news. """
    name = 'general'

    def parse(self, response):
        source_url = response.url
        news_collection = mongo_db.news
        count = total_count = 0
        for item in super().parse(response):
            total_count += 1
            doc = dict(item)
            doc['source_url'] = source_url

            # Insert the news into mongodb. XXX: Rely on mongo unique index for
            # deduplication.
            try:
                insert_result = news_collection.insert_one(doc)
            except pymongo.errors.DuplicateKeyError:
                continue

            count += 1
            request = scrapy.Request(item['url'], callback=self.store_content)
            request.meta['mongo_id'] = insert_result.inserted_id
            yield request

        self.logger.info('Dowloaded {}/{} news from {}'.format(count, total_count, source_url))
        
    def store_content(self, response):
        mongo_db.news.update_one({'_id': response.meta['mongo_id']},
                                 {'$set': {
                                     'compressed_content':gzip.compress(response.body)
                                 }})
