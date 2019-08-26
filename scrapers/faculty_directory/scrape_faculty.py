from bs4 import BeautifulSoup as soup
from typing import List
import requests
import string
import re

base_url = "http://facultyfinder.harvard.edu"


def main():
    faculty_links = get_faculty_links()
    id_finder_regex = re.compile('[0-9]+')
    faculty_dict = {}
    for link in faculty_links:
        faculty_id = int(id_finder_regex.search(link).group())
        faculty_info = get_faculty_info(link)
        faculty_dict[faculty_id] = faculty_info
    for faculty_info in faculty_dict:
        get_deep_details(faculty_info)
    upload_to_firebase(faculty_dict)


def get_faculty_links() -> List[dict]:
    faculty_links = []
    for letter in string.ascii_uppercase:
        offset = 0
        link_tags = True
        while link_tags:
            url = base_url + "search?name={}&offset={}".format(letter, offset)
            content = requests.get(url).content
            page_soup = soup(content, 'html.parser')
            person_regex = re.compile("^/display/person/.+$")
            # if we get an empty list, then we exit the loop
            link_tags = page_soup.find_all('a', href=person_regex)
            faculty_links += [tag.get('href') for tag in link_tags]
            offset += 100
    return faculty_links



def get_faculty_info(link) -> dict:
    content = requests.get(base_url + link).content
    page_soup = soup(content, 'html.parser')
    attribute_elements = page_soup.find_all('tr')
    result = {}
    faculty_name = soup.find('h2').text
    result['Name'] = faculty_name
    result['url_source'] = base_url + link
    for attribute_element in attribute_elements:
        attribute, value = attribute_element
        result[attribute.text] = value.text
    return result


# take an existing dict representing faculty and try to get more details
# basic strategy
## search these professors in faculty directory to try to find their emails and stuff
def get_deep_details(people):
    raise NotImplementedError()

# Take the list of people and upload them to firebase
## Shouldn't be too hard since you can just set documents from dicts
def upload_to_firebase(people):
    raise NotImplementedError()


if __name__ == "__main__":
    main()
