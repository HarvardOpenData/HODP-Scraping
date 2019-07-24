import dateutil
import typing as T
from functools import reduce

import pandas as pd
import numpy as np

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
