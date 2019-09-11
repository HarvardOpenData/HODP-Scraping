import os
import sys

from firebase_admin import initialize_app, credentials, firestore 

from backup_scripts.utils import backup_collection, get_backup_filename, datetime_converter


COLLECTIONS = ['sports-scores']

def init_scrapers_firebase():
    TEST_ENV = os.path.exists('hodp-scraping-secret-key.json')
    if TEST_ENV:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'hodp-scraping-secret-key.json'
    app_credentials = credentials.ApplicationDefault()

    return initialize_app(app_credentials,
                          name='hodp-scraping')

def main():
    output_dir = sys.argv[1] if len(sys.argv) > 1 else ""
    store = firestore.client(init_scrapers_firebase())

    for collection in COLLECTIONS:
        backup_collection(store, collection, output_dir)

if __name__ == "__main__":
    main()




