import os
import firebase_admin
from firebase_admin import storage
from firebase_admin import credentials
from firebase_admin import firestore
from google.oauth2 import id_token
from google.auth.transport import requests
from mockfirestore import *

def is_mock():
    return os.getenv("MOCK_FIRESTORE") == "TRUE"

def is_local():
    return os.getenv("LOCAL") == "TRUE"


def init_mock_scraping_firestore() -> firestore.firestore.Client:
    client = MockFirestore()
    return client

if is_mock():
    mock_scraping_client = init_mock_scraping_firestore()

def init_scraping_firebase():
    if is_mock():
        return
    # we're on the server, use the project ID
    if not is_local():
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred, {
            'projectId': "hodp-surveys",
        }, name = "scraping")
    # locally testing, we have some credential file
    else:
        cred = credentials.Certificate('scraping_creds.json')
        firebase_admin.initialize_app(cred, name = "scraping")

def get_scraping_firestore_client() -> firestore.firestore.Client:
    if is_mock():
        return mock_scraping_client
    app = firebase_admin.get_app("scraping")
    return firestore.client(app)