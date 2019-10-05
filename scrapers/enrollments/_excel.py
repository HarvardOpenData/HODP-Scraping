import json
from sys import argv, exit

import numpy as np
import pandas as pd

from .course import Course

def load_excel_file(file_name):
    return pd.read_excel(file_name)

def extract_courses(df):
    courses = []
    for _, series in df.iterrows():
        if len(series) > 1 and isinstance(series[0], str) and series[0].isdigit():
            title = series[1]
            department = series[4]
            instructor = series[5]
            ugrad = series[6]
            grad = series[7]

            courses.append(Course(title, department, instructor, ugrad, grad)._asdict())
    return courses

def scrape_excel(file_name):
    df = load_excel_file(file_name)
    return extract_courses(df)

