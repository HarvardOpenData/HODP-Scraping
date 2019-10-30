from bs4 import BeautifulSoup as soup
from typing import List
import requests
import string
import re
import json
import mockfirestore

base_url = "http://facultyfinder.harvard.edu"


def main():
    """
    Complete logic of the scraping program

    :return: None
    """
    faculty_members = get_faculty_ids(letters = ["A"], verbose = True)
    id_finder_regex = re.compile('[0-9]+')
    faculty_dict = {}
    for member in faculty_members:
        link = "http://facultyfinder.harvard.edu/display/person/{}".format(member["id"])
        faculty_id = int(id_finder_regex.search(link).group())
        faculty_info = get_faculty_info(link)
        faculty_dict[faculty_id] = faculty_info
    for faculty_id in faculty_dict:
        faculty_info = faculty_dict[faculty_id]
        faculty_info.update(get_deep_details(faculty_info))
    upload_to_firebase(faculty_dict)


def get_faculty_ids(letters = string.ascii_uppercase, verbose = False) -> List[str]:
    """

    :return: List of links of each faculty's page in facultyfinder
    """
    faculty_ids = []
    for letter in letters:
        offset = 0
        link_tags = True
        faculty_letter_ids = []
        while link_tags:
            url = base_url + "/search?name={}&offset={}".format(letter, offset)
            content = requests.get(url).content.decode("utf-8")
            # page_soup = soup(content, 'html.parser')
            person_regex = re.compile('<a href="\/display\/person\/(\d+?)\?name={}">(.+?)<\/a><\/td><td>(.*?)<\/td><td>(.*?)<\/td>'.format(letter))
            # if we get an empty list, then we exit the loop
            # link_tags = page_soup.find_all('a', href=person_regex)
            groups = person_regex.findall(content)
            if len(groups) == 0:
                link_tags = False
                break
            index = 0
            for group in groups:
                faculty_letter_ids.append({
                    "id" : group[0],
                    "name" :group[1],
                    "school" : group[2],
                    "title" : group[3]
                })
                index += 1
            offset += 100
            if verbose:
                print("scraped {} of {}".format(offset, letter))

        with open("{}_faculty.json".format(letter), "w+") as letter_output:
            json.dump(faculty_letter_ids, letter_output)
        print("Searched letter {}".format(letter))

    return faculty_ids


def get_faculty_info(link) -> dict:
    """

    :param link: link of faculty's page in facultyfinder
    :return: dictionary mapping each attribute to its value in this page
    """
    content = requests.get(base_url + link).content
    page_soup = soup(content, 'html.parser')
    attribute_elements = page_soup.find_all('tr')
    result = {}
    faculty_name = page_soup.find('h2').text
    result['Name'] = faculty_name
    result['url_source'] = base_url + link
    for attribute_element in attribute_elements:
        if len(attribute_element) == 2:
            attribute, value = attribute_element
        result[attribute.text] = value.text.replace('\u200b', '')
    return result


# take an existing dict representing faculty and try to get more details
# basic strategy
## search these professors in faculty directory to try to find their emails and stuff
def get_deep_details(faculty_info: dict) -> dict:
    """
    faculty
    :param faculty_info:
    :return:
    """
    raise NotImplementedError()

# Take the list of people and upload them to firebase
## Shouldn't be too hard since you can just set documents from dicts
def upload_to_firebase(faculty_info):
    with open("people.json", "w+") as output_file:
        json.dump(faculty_info, output_file)
    raise NotImplementedError()

def get_scraping_firestore():
    return mockfirestore.MockFirestore()

if __name__ == "__main__":
    main()
