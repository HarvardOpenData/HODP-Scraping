from scrapers.crime import scrape_crime
from scrapers.faculty_directory import scrape_faculty
from scrapers.gocrimson import scrape_gocrimson
from scrapers.grill_waits import scrape_grill_waits

def crime_scraper(data, context):
    scrape_crime.main()

def gocrimson_scraper(data, context):
    scrape_gocrimson.main()

def grill_waits_scraper(data, context):
    scrape_grill_waits.main()

