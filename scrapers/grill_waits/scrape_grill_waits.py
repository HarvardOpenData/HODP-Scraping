import requests
import json
import datetime
import sys
sys.path.append(".")
from scrapers.utils import auth
auth.init_scraping_firebase()

ORDER_URL = "https://mange.dining.harvard.edu/php/getData.php"
FORM_PAYLOAD = "formData%5BgetID%5D=waitTimes&formData%5Bhouses%5D%5B%5D=adams&formData%5Bhouses%5D%5B%5D=annenberg&formData%5Bhouses%5D%5B%5D=cabot&formData%5Bhouses%5D%5B%5D=currier&formData%5Bhouses%5D%5B%5D=dunster&formData%5Bhouses%5D%5B%5D=eliot&formData%5Bhouses%5D%5B%5D=kirkland&formData%5Bhouses%5D%5B%5D=leverett&formData%5Bhouses%5D%5B%5D=lowell&formData%5Bhouses%5D%5B%5D=mather&formData%5Bhouses%5D%5B%5D=pfoho&formData%5Bhouses%5D%5B%5D=quincy&formData%5Bhouses%5D%5B%5D=winthrop&userData%5BuserID%5D=11530&userData%5BisGuest%5D=0&userData%5BuserToken%5D=%242y%2410%24H2ebIAKXyaa3qfQTVfadUeAW%2FAiDtmanjcRfeVB1.qK9v4g8sjEne&userData%5BuserType%5D=user&userData%5BtimeStamp%5D=1569358524&otherData%5Blocation%5D=&otherData%5BuserAgent%5D=Mozilla%2F5.0+(X11%3B+Linux+x86_64)+AppleWebKit%2F537.36+(KHTML%2C+like+Gecko)+Chrome%2F77.0.3865.90+Safari%2F537.36&otherData%5Bvendor%5D=Google+Inc.&otherData%5Blanguage%5D=en-US"
HEAD = {'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'https://mange.dining.harvard.edu',
    'Referer': 'https://mange.dining.harvard.edu/pages/grillorders.html',
    'Sec-Fetch-Mode': 'cors',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
    'X-Requested-With' : 'XMLHttpRequest'}
COLLECTION_NAME = "grill-orders"


def scrape_grill_waits():
    try:
        s = requests.session()
        result = s.post(ORDER_URL, data=FORM_PAYLOAD, headers=HEAD)
        wait_dict = json.loads(result.content.decode('utf-8'))
        wait_dict['got_response'] = True
        return wait_dict
    except:
        return {"got_response": False}


def main():
    # uncomment below for local testing
    #cred = credentials.Certificate("/home/petey/Documents/Harvard/hodp/dhall_scrape/testgrill-76d2a-firebase-adminsdk-i3132-9d8c405083.json")
    #app = initialize_app(cred, name='testgrill-76d2a')
    #store = firestore.client(app)
    store = auth.get_scraping_firestore_client()
    collec = store.collection(COLLECTION_NAME)
    data = scrape_grill_waits()
    dt = datetime.datetime.now(tz=datetime.timezone('US/Eastern'))
    if dt.hour < 17:
        meal = "Lunch"
    else:
        meal = "Dinner"
    doc = collec.document(dt.strftime("%m_%d_%Y") + "_" + meal)
    if not doc.get().exists:
        doc.set({'meal': meal, 'date': dt})
    sub_collec = doc.collection("snapshots")
    dt_str = dt.strftime("%H:%M:%S")
    data['time'] = dt
    sub_collec.document(dt_str).set(data)

if __name__ == "__main__":
    main()
    #store = auth.get_scraping_firestore_client()
    #collec = store.collection(COLLECTION_NAME)
    #print([d.get().to_dict() for d in collec.list_documents()])





