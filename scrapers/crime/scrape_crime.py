import datetime
from urllib.error import HTTPError

import camelot
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from koala_cron.monitor import build_job

# bad practice but yolo
from transformations import *

cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
    'projectId': "hodp-scraping",
})

db = firestore.client()

crimes_ref = db.collection(u"crime-logs")
test_arr = []
# Extract, clean, and insert data into db


def scrape(url):
    """
        known edge cases:
            case where address is only one line: DONE
                 where 12am is sometimes written as 0:xx am: DONE
                 where description is broken up across two pages: NOT DONE

    """
    tables = camelot.read_pdf(url, pages="1-end")
    row_num = 0

    for table in tables:
        clean_dataframe = clean_and_organize_data(table.df)
        transformed_dataframe = apply_transformations(dataframe=clean_dataframe,
                                                      clean_and_organize_data,
                                                      clean_one_liners,
                                                      remove_new_lines,
                                                      convert_to_datetime)

        for _, report_series in transformed_dataframe.iterrows():
            report = report_series.to_dict()
            db.collection(u'crime-logs').add(report)
            row_num += 1


# Find latest date
@build_job
def main():
    query = crimes_ref.order_by(
        u'reported', direction=firestore.Query.DESCENDING).limit(1)
    results = query.stream()

    for doc in results:
        latest_time = (doc.to_dict())["reported"]
        last_date = datetime.datetime(
            year=latest_time.year, month=latest_time.month, day=latest_time.day)
        last_date += datetime.timedelta(days=1)
        cur_date = datetime.datetime.now()
        print("Hello")
        while last_date < cur_date:
            day = str(last_date.day)
            month = str(last_date.month)
            year = str(last_date.year - 2000)
            if(len(month) < 2):
                month = "0" + month
            if(len(day) < 2):
                day = "0" + day
            url = "https://www.hupd.harvard.edu/files/hupd/files/" + month + day + year + ".pdf"
            # Scrape each url
            try:
                scrape(url)
            except HTTPError:
                print("Error")
            last_date += datetime.timedelta(days=1)

    print("Scrape crime Logs")


if __name__ == "__main__":
    m = Monitor(
        "https://hooks.slack.com/services/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")
    m.attach_job(main, job_name="scrape_crime")()


# scrape("https://www.hupd.harvard.edu/files/hupd/files/040219.pdf")
