import beautifulsoup4 as bsoup
import string
from typing import List
from urllib.request import urlopen

# downloads html from url
def download_html(url : str) -> str:
    return urlopen(url).read().decode("utf-8")

# get details found on first search page:
## first and last name
## url to more details
## school
## title
# basic strategy:
## Loop through each letter of the alphabet
## Loop through increments of 100 offset in the url
## Get all of the links to faculty pages
def get_outline_data() -> List[dict]:
    all_outlines = []
    for letter in string.ascii_uppercase:
        offset = 0
        while True: 
            url = "http://facultyfinder.harvard.edu/search?name={}&offset={}".format(letter, offset)
            page_outlines = get_links_on_finder_page(url)
            if len(page_outlines) == 0:
                break
            all_outlines += page_outlines
            offset += 100
    return all_outlines

def get_outlines_on_finder_page(url) -> List[dict]:
    raise NotImplementedError()
# takes a list of urls on faculty finder and gets basic info about faculty member from that page
# Not sure we even need this
# basic strategy:
## Go to each link, create dictionary with the corresponding info
## Return a list of dictionaries with all the info we can get about each prof here
## or should we return a dictionary of dictionaries with the professor's name as the key?
def get_basic_details(links : List[str]):
    raise NotImplementedError()

# take an existing dict representing faculty and try to get more details
# basic strategy
## search these professors in faculty directory to try to find their emails and stuff
def get_deep_details(people):
    raise NotImplementedError()

# Take the list of people and upload them to firebase
## Shouldn't be too hard since you can just set documents from dicts
def upload_to_firebase(people):
    raise NotImplementedError()