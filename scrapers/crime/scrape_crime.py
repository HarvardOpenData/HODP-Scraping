import camelot
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import datetime
from datetime import timedelta
import re

cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
    'projectId': "hodp-scraping",
})

db = firestore.client()

crimes_ref = db.collection(u"crime-logs")
test_arr = []
# Extract, clean, and insert data into db


def scrape(url):
    tables = camelot.read_pdf(url, pages="1-end")
    row_num = 0

    for table in tables:
        for row in table.data[1:]:
            # Check whether it's info or description
            if row_num % 2 == 0:
                clean_row = [x for x in row if len(x) > 0]
                # Account for the case where description is broken up across two pages
                if re.search(r'\d+/\d+/\d+', clean_row[0]) and not re.search(r'U|update', clean_row[0]):
                    # Account for case where all info is read into one element in a list
                    if len(clean_row) == 1:
                        data = clean_row[0].splitlines()
                        # Account for when 12am is sometimes written as 0:xx am
                        reported = (data[0] + "\n" + data[5]
                                    ).replace("\n0:", "\n12:")
                        occurred = data[1] + "\n" + data[6]
                        # Account for when address is one line only
                        if len(data) == 7:
                            address = data[2] + " " + data[7]
                        else:
                            address = data[2].replace("\n", "")
                        d_type = data[3]
                        status = data[4]
                        date_time_obj = datetime.datetime.strptime(
                            reported, '%m/%d/%y\n%I:%M %p')
                        report = {"reported": date_time_obj, "type": d_type, "occurred": occurred,
                                  "address": address, "status": status}
                    # Regular case (each cell read in as separate element)
                    else:
                        clean_row[3] = clean_row[3].replace("\n", " ")
                        # Account for when 12am is sometimes written as 0:xx am
                        clean_row[0] = clean_row[0].replace("\n0:", "\n12:")
                        date_time_obj = datetime.datetime.strptime(
                            clean_row[0], '%m/%d/%y\n%I:%M %p')
                        report = {"reported": date_time_obj, "type": clean_row[1], "occurred": clean_row[2],
                                  "address": clean_row[3], "status": clean_row[4]}
                    row_num += 1
                else:
                    pass
            else:
                clean_row = [x for x in row if len(x) > 0]
                report["description"] = clean_row[0]
                db.collection(u'crime-logs').add(report)
                row_num += 1


def scrape():
    # Find latest date
    query = crimes_ref.order_by(
        u'reported', direction=firestore.Query.DESCENDING).limit(1)
    results = query.stream()

    for doc in results:
        latest_time = (doc.to_dict())["reported"]
        last_date = datetime.datetime(
            year=latest_time.year, month=latest_time.month, day=latest_time.day)
        last_date += timedelta(days=1)
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
            except:
                print("Error")
            last_date += timedelta(days=1)

    print("Scrape crime Logs")


# scrape("https://www.hupd.harvard.edu/files/hupd/files/040219.pdf")
