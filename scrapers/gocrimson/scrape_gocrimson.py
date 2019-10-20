import logging
from functools import partial

from twisted.internet import reactor
from scrapy import Spider, log, signals, Item, Field
from scrapy.crawler import CrawlerRunner
from scrapy.loader import ItemLoader
from scrapy.utils.log import configure_logging
from firebase_admin import credentials, initialize_app, firestore

from koala_cron.monitor import build_job

gocrimson_logger = logging.getLogger("gocrimson_logger")
gocrimson_logger.setLevel("INFO")

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


oApp = initialize_app(credentials.ApplicationDefault(),
                      name='hodp-scraping'
                      )


class TeamsCrawlerRunner(CrawlerRunner):
    """
    Crawler object that collects items and returns output after finishing crawl.
    """

    def crawl(self, crawler_or_spidercls, *args, **kwargs):
        self.settings = None
        self.COLLECTION_NAME = 'sports-scores'
        self.store = firestore.client(oApp)
        self.collection_ref = self.store.collection(self.COLLECTION_NAME)
        self.batch = self.store.batch()

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
        doc_name = (
            f"{item['team']}-{item['season']}").replace('\'', '').replace(' ', '-').lower()
        doc_ref = self.collection_ref.document(doc_name)
        validated = True
        for data in item:
            if not data:
                validated = False
        if validated:
            self.batch.set(doc_ref, dict(item))
            gocrimson_logger.info(f'{doc_name} added to batch.')
        return item

    def return_items(self, result):
        self.batch.commit()
        gocrimson_logger.info(
            f'Successfully committed to collection {self.COLLECTION_NAME}.')
        return "Teams successfully scraped"


def return_spider_output(output):
    """
    :param output: items scraped by CrawlerRunner
    :return: json with list of items
    """
    # this just turns items into dictionaries
    # you may want to use Scrapy JSON serializer here
    return output


configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})


gocrimson_job = partial(build_job,
                        endpoint="https://hooks.slack.com/services/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",
                        job_name="scrape gocrimson")


@gocrimson_job
def main():
    runner = TeamsCrawlerRunner()
    spider = TeamsSpider()
    deferred = runner.crawl(spider)
    deferred.addBoth(lambda _: reactor.stop())
    reactor.run()


if __name__ == "__main__":
    main()
