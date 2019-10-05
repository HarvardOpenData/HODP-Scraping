import json
import sys
import collections as col
from time import sleep
from itertools import *

import numpy as np
from tabula import read_pdf

Course = col.namedtuple("Course", ["title", "department", "instructor", "ugrad", "grad"])
def contains_digits(text):
    return any(c.isdigit() for c in text)

def to_string(iterable):
    return ''.join(iterable).strip()

def parse_series(series):
    try:
        if len(series) == 7:
            if not isinstance(series.iloc[1], str):
                tokens = series.iloc[0].split()
                title, instructor = tokens[0], tokens[-1]
            elif contains_digits(series.iloc[1]):
                tokens = series.iloc[1].split()
                course_number, instructor = tokens[0], tokens[-1]
                title = series.iloc[0] + ' ' + course_number
            else:
                title = series.iloc[0]
                instructor = series.iloc[1]
            ugrad = series.iloc[2]
            grad = series.iloc[3]
        elif len(series) == 8:
            if not isinstance(series.iloc[1], str) and not isinstance(series.iloc[2], str):
                    title = series.iloc[0]
                    instructor = ""
            elif not isinstance(series.iloc[2], str): 
                course_number, instructor = series.iloc[1].split()
                title = series.iloc[0] + course_number
            elif isinstance(series.iloc[2], str) and contains_digits(series.iloc[2]):
                course_number, instructor = series.iloc[2].split()
                title = series.iloc[0] + course_number
            else:
                if not isinstance(series.iloc[1], str):
                    title = series.iloc[0]
                else:
                    title = series.iloc[0] + ' ' + series.iloc[1]
                instructor = series.iloc[2] if isinstance(series.iloc[1], str) else ""
            ugrad = series.iloc[3]
            grad = series.iloc[4] 
        else:
            return None
    except:
        return None
    title = chain(to_string(takewhile(lambda c: not c.isdigit(), title)), ' ', to_string(dropwhile(lambda c: not c.isdigit(), title)))
    title = ''.join(title)
    return Course(title, "", instructor, ugrad, grad)._asdict()

def get_tables(url):
    tables = read_pdf(url, pages='all', multiple_tables=True)
    return tables

def clean_tables(tables):
    for table in tables:
        yield table.dropna(axis=0, how='all').dropna(axis=1, how='all')

def extract_courses(tables):
    dropped = 0
    courses = []
    for table in tables:
        for i, series in table.iterrows():
            result = parse_series(series)
            if result is None:
                dropped += 1
            else:
                courses.append(result)
    return courses

def scrape_pdf(url):
    tables = clean_tables(get_tables(url))
    return extract_courses(tables)

