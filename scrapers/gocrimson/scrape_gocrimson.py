import logging

from twisted.internet import reactor
from scrapy import Spider, signals, Item, Field
from scrapy.crawler import CrawlerRunner
from scrapy.loader import ItemLoader
from firebase_admin import credentials, initialize_app, firestore

from sql.engine import init_session
from sql.models import Score

gocrimson_logger = logging.getLogger(__name__)
c_handler = logging.StreamHandler()
c_handler.setLevel(logging.DEBUG)
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
gocrimson_logger.addHandler(c_handler)
gocrimson_logger.setLevel(logging.DEBUG)


# TODO: modularize code
URLS = [
    "https://www.gocrimson.com/sports/bsb/archive",
    "https://www.gocrimson.com/sports/mbkb/archive",
    "https://www.gocrimson.com/sports/fball/archive",
    "https://www.gocrimson.com/sports/mice/archive",
    "https://www.gocrimson.com/sports/mlax/archive",
    "https://www.gocrimson.com/sports/msoc/archive",
    "https://www.gocrimson.com/sports/mvball/archive",
    "https://www.gocrimson.com/sports/wbkb/archive",
    "https://www.gocrimson.com/sports/fh/archive",
    "https://www.gocrimson.com/sports/wice/archive",
    "https://www.gocrimson.com/sports/wlax/archive",
    "https://www.gocrimson.com/sports/wsoc/archive",
    "https://www.gocrimson.com/sports/sball/archive",
    "https://www.gocrimson.com/sports/wvball/archive"
]


class OverallScoresItem(Item):
    team = Field()
    season = Field()
    overall = Field()
    conference = Field()
    streak = Field()
    home = Field()
    away = Field()
    neutral = Field()


class TeamsSpider(Spider):
    name = 'teams'
    allowed_domains = ['gocrimson.com']
    start_urls = URLS

    def parse(self, response):
        stats = response.xpath("//a[contains(@href, '/teams/harvard')]")
        for url in stats:
            yield response.follow(url, callback=self.parse_overall)

    def parse_overall(self, response):
        gocrimson_logger.debug(f'scraping {response.url}')
        table = response.css('div.half:nth-child(1) > table:nth-child(1)')

        # Load items
        scores = OverallScoresItem()

        scores['team'] = response.css(
            '.secondary-nav > h1:nth-child(1) > a:nth-child(1)::text').get()
        scores['season'] = response.url.split('/')[-3]

        # Could use a loop probably
        scores['overall'] = table.css(
            'tr:nth-child(2) > td:nth-child(2)::text').get()
        scores['conference'] = table.css(
            'tr:nth-child(3) > td:nth-child(2)::text').get()
        scores['streak'] = table.css(
            'tr:nth-child(4) > td:nth-child(2)::text').get()
        scores['home'] = table.css(
            'tr:nth-child(5) > td:nth-child(2)::text').get()
        scores['away'] = table.css(
            'tr:nth-child(6) > td:nth-child(2)::text').get()
        scores['neutral'] = table.css(
            'tr:nth-child(7) > td:nth-child(2)::text').get()

        yield scores


class TeamsCrawlerRunner(CrawlerRunner):
    """
    Crawler object that collects items and returns output after finishing crawl.
    """

    def crawl(self, crawler_or_spidercls, *args, **kwargs):
        self.settings = None
        self.session = init_session("scrape-test", local=True)
        # create crawler (Same as in base CrawlerProcess)
        crawler = self.create_crawler(crawler_or_spidercls)

        # handle each item scraped
        crawler.signals.connect(self.item_scraped, signals.item_scraped)

        # create Twisted.Deferred launching crawl
        dfd = self._crawl(crawler, *args, **kwargs)

        # add callback - when crawl is done cal return_items
        dfd.addCallback(self.return_items)
        return dfd

    def item_scraped(self, item, response, spider):
        gocrimson_logger.debug("processing item")

        data = Score(**item)

        query = self.session.query(Score).filter()

        # if query.count():
        qry = data
        self.session.merge(qry)
        gocrimson_logger.debug(f'item merged.')
        # else:
        #     self.session.add(data)
        #     gocrimson_logger.debug(f'item added.')
        self.session.commit()

        return item

    def return_items(self, result):
        self.session.commit()
        gocrimson_logger.debug(
            f'Successfully committed to db.')
        self.session.close()
        return "Teams successfully scraped"


def return_spider_output(output):
    """
    :param output: items scraped by CrawlerRunner
    :return: json with list of items
    """
    # this just turns items into dictionaries
    # you may want to use Scrapy JSON serializer here
    return output


def main():
    runner = TeamsCrawlerRunner()
    spider = TeamsSpider()
    deferred = runner.crawl(spider)
    deferred.addBoth(lambda _: reactor.stop())
    reactor.run()


if __name__ == "__main__":
    main()
