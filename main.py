from flask import Flask
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from scrapers.crime import scrape_crime

app = Flask (__name__)

cred = credentials.Certificate('hodp-scraping-b7a68d6b8324.json')
firebase_admin.initialize_app(cred)

'''
cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
  'projectId': "hodp-scraping",
})'''

db = firestore.client()

@app.route('/')
def default():
    return "HODP Scraping Google AppEngine API"

@app.route('/scrape/crime')
def crime():
    return scrape_crime(db)