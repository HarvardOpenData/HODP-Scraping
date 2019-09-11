import os
import sys
import json
from datetime import datetime

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from ..utils import backup_collection, get_backup_filename, datetime_converter

def main():
    output_dir = ""
    if len(sys.argv) > 1:
        output_dir = sys.argv[1]
    init_survey_firebase()
    db = get_survey_firestore_client()
    backup_collection(db, "emails", output_dir)
    backup_collection(db, "responses", output_dir)

def init_survey_firebase():
    # we're on the server, use the project ID
    if not os.path.exists("survey_creds.json"):
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred, {
            'projectId': "hodp-surveys",
        })
    # locally testing, we have some credential file
    else:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'survey_creds.json'
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred)

def get_survey_firestore_client():
    return firestore.client()

if __name__ == "__main__":
    main()
