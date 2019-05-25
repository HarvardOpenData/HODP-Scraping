from flask import Flask, redirect

# Scraping-related imports
from scrapers.crime import scrape_crime
app = Flask(__name__)


@app.route('/')
def index():
    return "there's nothing here"


@app.route('/scrape/crime')
def scrapeCrime():
    scrape_crime.scrape()
    return "scraped crime"


@app.route('/scrape/gocrimson')
def scrapeGocrimson():
    # Trigger the "gocrimson" GCloud function
    return redirect("https://us-central1-hodp-scraping.cloudfunctions.net/gocrimson")


# for dev testing
if __name__ == '__main__':
    app.run('localhost', 3000)
