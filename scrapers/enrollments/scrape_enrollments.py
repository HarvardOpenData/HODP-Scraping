import os
import json
import collections as col

import requests
from bs4 import BeautifulSoup

from ._pdf import scrape_pdf
from ._html import scrape_html
from ._excel import scrape_excel

ARCHIVES_URL = 'https://registrar.fas.harvard.edu/faculty-staff/courses/enrollment/archived-course-enrollment-reports'

def get_available_datasets():
    def create_term(dataset_link):
        name = dataset_link.text
        src = dataset_link["href"]
        return name, src

    soup = BeautifulSoup(requests.get(ARCHIVES_URL).text, features='lxml')
    dataset_links = soup.select(".field-item a")
    return [create_term(link) for link in dataset_links]
	
def disambiguate_type(dataset):
    name, src = dataset
    _, ext = os.path.splitext(src)

    courses = []
    if ext == '.pdf':
        courses = scrape_pdf(src)
    elif ext == '.html':
        courses = scrape_html(src)
    elif ext == '.xlsx':
        courses = scrape_excel(src)
    else:
        raise Exception(f"unknown ext {ext}")

    with open(name + '.json', 'w+') as fp:
        json.dump(courses, fp)
    
if __name__ == "__main__":
    for dataset in get_available_datasets():
        disambiguate_type(dataset)
