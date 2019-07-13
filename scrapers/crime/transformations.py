import dateutil
import typing as T
from functools import reduce

import pandas as pd

LABELS = ("reported", "type", "occurred",
          "address", "status", "description")


def apply_transformations(dataframe: pd.DataFrame,
                          *functions) -> pd.DataFrame:
    """
        Generic reducer accepting functions to be applied to dataframe.

        Returns:
            A dataframe with all functions applied.
    """
    return reduce(lambda df, callback: df.apply(callback, axis=1),
                  functions,
                  dataframe)


def convert_to_datetime(series: pd.Series) -> pd.Series:
    series["reported"] = dateutil.parser.parse(series["reported"])
    return series


def remove_new_lines(series: pd.Series) -> pd.Series:
    def remove_new_lines(str): return str.replace('\n', ' ')
    return series.apply(remove_new_lines)


def clean_one_liners(series: pd.Series) -> pd.Series:
    if all(series[label] != "" for label in LABELS):
        pass
    else:
        lines = list(map(lambda str: str.strip(),
                         series["reported"].split("\n")))
        if len(lines) != 7:
            series = pd.Series([])
        else:
            reported_1, occurred_1, address, incident_type, status, reported_2, occurred_2 = lines

            series["reported"] = reported_1 + "\n" + reported_2
            series["occurred"] = occurred_1 + "\n" + occurred_2
            series["address"] = address
            series["type"] = incident_type
            series["status"] = status
    return series


def zip_single(iterable: T.Iterable[T.Any]):
    """
        Zips together every two elements in an iterable.
    """
    first, second, *rest = iterable
    if rest:
        return [(first, second)] + zip_single(rest)
    else:
        return [(first, second)]


def clean_and_organize_data(dataframe: pd.DataFrame) -> pd.DataFrame:
    # Remove column headings
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
        info = info.drop([4, 6])
        description = description.drop(list(range(1, 7)))
        combined_series = info.append(description, ignore_index=True)

        # Convert the series into a dataframe for the sake of labelling it
        df = pd.DataFrame(combined_series)
        labeled_data = df.rename(mapper).transpose()
        return labeled_data

    report_dfs = map(combine_report_info, info_report_list)
    merged_reports = reduce(lambda merged, df: merged.merge(df, how="outer"),
                            report_dfs)
    return merged_reports
