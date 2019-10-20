import datetime
import logging
from urllib.error import HTTPError
from functools import partial

import camelot
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
# from koala_cron.monitor import build_job

# bad practice but yolo
# from transformations import *

logger = logging.getLogger("crime-logger")
logger.setLevel("INFO")

cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
    'projectId': "hodp-scraping",
})

db = firestore.client()

crimes_ref = db.collection(u"crime-logs")
test_arr = []
# Extract, clean, and insert data into db


def scrape(url):
    logger.info("Received content from {}".format(url))
    tables = camelot.read_pdf(url, pages="1-end")
    row_num = 0

    processed_tables = []
    for i, table in enumerate(tables):
        df = table.df
        height, width = df.shape

        """
           Case below handles when first entry is the continuation of a description from the last
           This is inferred from whether the content in df.iloc[1][0] contains
           a period, a character that currently only appears in descriptions
        """
        if "." in df.iloc[1][0]:
            trailing_description = df.iloc[1][0]
            df = df[2:]

            prev_table = processed_tables[i - 1]
            last_index = prev_table.index[-1]
            prev_description = prev_table.loc[last_index,
                                              "description"]
            prev_table.loc[last_index,
                           "description"] = prev_description + " " + trailing_description

            processed_tables[i - 1] = prev_table

        if not df.empty:
            clean_dataframe = clean_and_organize_data(df)

            transformed_dataframe = apply_transformations(clean_dataframe,
                                                          clean_one_liners,
                                                          remove_new_lines,
                                                          convert_to_datetime)
            processed_tables.append(transformed_dataframe)

        for _, report_series in transformed_dataframe.iterrows():
            report = report_series.to_dict()
            db.collection(u'crime-logs').add(report)
            logger.info("Added {} to collection crime-logs".format(report))
            row_num += 1


# Find latest date
#crime_job = partial(build_job,
#                    endpoint="https://hooks.slack.com/services/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",
#                    job_name="scrape crime")


# @crime_job
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
                logger.info("Attempting to scrape {}".format(url))
                scrape(url)
            except HTTPError:
                logger.warning(
                    "Querying {} returned an HTTP error!".format(url))
            last_date += datetime.timedelta(days=1)

    logger.info("Exiting")


if __name__ == "__main__":
    main()

LABELS = ("reported", "type", "occurred",
          "address", "status", "description")


def apply_transformations(dataframe: pd.DataFrame,
                          *functions) -> pd.DataFrame:
    """
        Generic reducer accepting functions to be applied to dataframe.

        Returns:
            A dataframe with all functions applied.
    """
    def apply_func(df, callback):
        return df.apply(callback, axis=1)

    return reduce(apply_func,
                  functions,
                  dataframe)


def convert_to_datetime(series: pd.Series) -> pd.Series:
    time_str = series["reported"]
    if isinstance(time_str, str):
        series["reported"] = dateutil.parser.parse(time_str)
    return series


def remove_new_lines(series: pd.Series) -> pd.Series:
    def remove_new_lines(str): return str.replace('\n', ' ')
    return series.apply(remove_new_lines)


def clean_one_liners(series: pd.Series) -> pd.Series:

    lines = list(map(lambda str: str.strip(),
                     series["reported"].split("\n")))

    new_series = pd.Series([])

    if len(lines) == 9:
        reported_1, occurred_1, address_1, incident_type_1, status, reported_2, occurred_2, address_2, incident_type_2 = lines

        new_series["reported"] = reported_1 + "\n" + reported_2
        new_series["occurred"] = occurred_1 + "\n" + occurred_2
        new_series["address"] = address_1 + address_2
        new_series["type"] = incident_type_1 + incident_type_2
        new_series["status"] = status
        new_series["description"] = series["description"]

    elif len(lines) == 8:
        reported_1, occurred_1, address_1, incident_type, status, reported_2, occurred_2, address_2 = lines

        new_series["reported"] = reported_1 + "\n" + reported_2
        new_series["occurred"] = occurred_1 + "\n" + occurred_2
        new_series["address"] = address_1 + address_2
        new_series["type"] = incident_type
        new_series["status"] = status
        new_series["description"] = series["description"]

    elif len(lines) == 7:
        reported_1, occurred_1, address, incident_type, status, reported_2, occurred_2 = lines

        new_series["reported"] = reported_1 + "\n" + reported_2
        new_series["occurred"] = occurred_1 + "\n" + occurred_2
        new_series["address"] = address
        new_series["type"] = incident_type
        new_series["status"] = status
        new_series["description"] = series["description"]
    else:
        new_series = series

    return new_series


def zip_single(iterable: T.Iterable[T.Any]):
    """
        Zips together every two elements in an iterable.
    """
    try:
        first, second, *rest = iterable
    except ValueError:
        first, *rest = iterable
        placeholders = [" "]
        second = pd.Series(data=placeholders)

    if rest:
        return [(first, second)] + zip_single(rest)
    else:
        return [(first, second)]


def clean_and_organize_data(dataframe: pd.DataFrame) -> pd.DataFrame:
    # Remove column headings
    if dataframe.iloc[0][0].startswith("Date & Time"):
        dataframe = dataframe.iloc[1:]

    mapper = {num: label for num, label in enumerate(LABELS)}

    # zip_single is used to pair each report with its description
    info_report_list = zip_single(
        [series for _, series in dataframe.iterrows()])

    def combine_report_info(
            info_report_tuple: T.List[T.Tuple[pd.Series]]) -> pd.DataFrame:
        """
            Methods like .dropna() don't seem to work here, so this hard-coded
            solution removes missing/junk values from every report series.
        """
        info, description = info_report_tuple
        info = pd.Series(info.replace('', np.nan).dropna().values)
        description = pd.Series(description.replace(
            '', np.nan).dropna().values, index=[5])
        combined_series = info.append(description)

        # Convert the series into a dataframe for the sake of labelling it
        df = pd.DataFrame(combined_series)
        labeled_data = df.rename(mapper).transpose()
        return labeled_data

    report_dfs = map(combine_report_info, info_report_list)
    merged_reports = reduce(lambda merged, df: merged.merge(df, how="outer"),
                            report_dfs).fillna('')
    return merged_reports