import collections as col
from time import sleep

import requests
import pandas as pd
from bs4 import BeautifulSoup

Course = col.namedtuple("Course", ["title", "department", "instructor", "ugrad", "grad"])

def get_soup(url):
    response = requests.get(url)
    return BeautifulSoup(response.content, features='lxml')

def parse_paragraph_based(soup):
    def filter_semicolons(text):
        tokens = text.split(':')
        if len(tokens) <= 1:
            return text.strip()
        return tokens[1].strip()

    def is_course_line(text):
        if text is None:
            return False
        tokens = text.split(' ')
        if len(tokens) <= 1:
            return False
        first = tokens[0]
        is_course = first.isupper()
        return is_course

    def construct_course(course_line):
        tokens = list(map(lambda token: filter_semicolons(token), course_line.split('\t')))
        if len(tokens) == 6:
            title, instructor, ugrad, gsas, _, total = tokens
            course = Course(title, "", instructor, ugrad, gsas)
            return course._asdict()
        return None
        
    lines = soup.find_all('p')
    courses = filter(lambda line: is_course_line(line.text), lines)
    courses = map(lambda course: construct_course(course.text), courses)
    return list(courses)

def parse_table_based(soup):
    def is_course_row(tr_soup):
        first_td = tr_soup.find("td")
        if first_td is None:
            return False
        first_td = first_td.text.split(' ')
        if len(first_td) <= 1:
            return False
        return first_td[0].isupper()

    def construct_course(course_tr):
        row_items = list(map(lambda td: td.text, course_tr.find_all("td")))
        if len(row_items) == 6:
            title, instructor, ugrad, gsas, _, total = row_items
            course = Course(title, "", instructor, ugrad, gsas)
            return course._asdict()
        return None

    tables = soup.find("table")
    courses = []
    for row in tables.find_all("tr"):
        if is_course_row(row):
            courses.append(construct_course(row))

    return courses

def scrape_html(url):
    soup = get_soup(url)
    if soup.find("table") is None:
        return parse_paragraph_based(soup)
    else:
        return parse_table_based(soup)

