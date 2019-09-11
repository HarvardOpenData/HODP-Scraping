import os
import json
from datetime import datetime

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

def get_backup_filename(collection_name):
    today = datetime.today()
    return "{}_{}{}{}_backup.json".format(collection_name, str(today.year).zfill(4), str(today.month).zfill(2), str(today.day).zfill(2))

def datetime_converter(o):
    if isinstance(o, datetime):
        return o.__str__()


