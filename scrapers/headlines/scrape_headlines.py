"""A simpler project demonstrating how a scraper might be organized"""
import functools
import collections as col
from typing import List
from datetime import datetime

import requests
from dateutil import parser
from bs4 import BeautifulSoup
from firebase_admin import credentials, initialize_app, firestore

Headline = col.namedtuple("Headline", ["title", "url"])
Article = col.namedtuple("Article", ["title", "url", "publication", "observed_on", "contributors", "text"])
CRIMSON_URL = "https://www.thecrimson.com"

def get_most_read_articles() -> List[Headline]:
    def construct_article(article_li):
        title = article_li.find(class_="article-listitem-text").text.strip()
        url = article_li.find("a")["href"]
        return Headline(title, CRIMSON_URL + url)

    response = requests.get(CRIMSON_URL)
    soup = BeautifulSoup(response.text, features="lxml")
    headlines_html = soup.find(id="most-read-box").find_all(class_="article-listitem")

    return [construct_article(article_li) for article_li in headlines_html]

def scrape_article(article: Headline) -> Article:
    title = article.title
    url = article.url
    
    response = requests.get(url)
    soup = BeautifulSoup(response.text)
    publication = parser.parse(soup.find(class_="article-date")["datetime"])
    observed_on = datetime.now()

    contributors_soup = soup.find(class_="article-byline").find_all("a")
    contributors = [contributor_a.text for contributor_a in contributors_soup]
    
    paragraphs = soup.find(id="text").find_all("p")
    text = functools.reduce(lambda text, paragraph: text + paragraph.text, paragraphs, "")
    return Article(title, url, publication, observed_on, contributors, text)

def commit_articles_to_firebase(articles: List[Article]): 
    store = get_store()
    batch = store.batch()
    collection_ref = store.collection("headlines")

    def add_to_batch(document_name, article):
        article = article.as_dict()
        doc_ref = collection_ref.document(document_name)
        batch.set(doc_ref, article)

    for article in articles:
        add_to_batch(article.title, article)

def get_store():
    app = initialize_app(credentials.ApplicationDefault(),
                         name='hodp-scraping')
    return firestore.client(app)


