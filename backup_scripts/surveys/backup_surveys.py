import firebase_admin
import os
import sys
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime
import json

def main():
    output_dir = ""
    if len(sys.argv) > 1:
        output_dir = sys.argv[1]
    init_survey_firebase()
    db = get_survey_firestore_client()
    backup_collection(db, "emails", output_dir)
    backup_collection(db, "responses", output_dir)

def backup_collection(db, collection_name, output_dir):
    collection_ref = db.collection(collection_name)
    docs = collection_ref.stream()
    dicts = {}
    for doc in docs:
        dicts[doc.id] = doc.to_dict()
    output_json = json.dumps(dicts, default=datetime_converter)
    output_filename = get_backup_filename(collection_name)
    with open(os.path.join(output_dir, output_filename), "w+") as f:
        f.write(output_json)

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

def get_backup_filename(collection_name):
    today = datetime.today()
    return "{}_{}{}{}_backup.json".format(collection_name, str(today.year).zfill(4), str(today.month).zfill(2), str(today.day).zfill(2))

def datetime_converter(o):
    if isinstance(o, datetime):
        return o.__str__()

if __name__ == "__main__":
    main()