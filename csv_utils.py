"""
Csv utilities
"""

import csv
import os

from core.nova_tag_list import NovaTagList
from git_utils import get_git_tag_url

DEFAULT_CSV_DIRECTORY = "artifacts"
DEFAULT_CSV_OUTPUT = "components-output.csv"


def export_tags_to_csv(
    data: list[dict[str, str]],
    path: str = DEFAULT_CSV_DIRECTORY,
    file_name: str = DEFAULT_CSV_OUTPUT,
) -> str:
    """
    Export tags to csv file

    :param data: data to export
    :param path: path to the directory where the file will be created
    :param file_name: name of the file
    :return: path to the created file
    """
    if file_name is None:
        file_name = DEFAULT_CSV_OUTPUT

    if path is None:
        path = DEFAULT_CSV_DIRECTORY

    if not os.path.exists(path):
        os.makedirs(path)

    file_path = os.path.join(path, file_name)

    with open(file_path, "w", newline="", encoding="utf-8") as csv_file:
        fieldnames = ["component", "tag", "date", "url"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

    return file_path


GitTagCsvRow = tuple[str, str, str, str]


def map_to_csv_rows(source: NovaTagList) -> list[GitTagCsvRow]:
    """
    Maps nova tag list into a sorted list of tuples
    where each tuple represents an information about a tag.

    :param source: NovaTagList instance
    :return: List of tuples sorted by tag date with tag information
    of the following format:
    (component name, tag name, tag date, tag url)
    """
    if source.component.repo is None:
        raise ValueError(f"{source.component.name} repo is not specified")

    repo = source.component.repo

    return list(
        (
            (
                source.component.name,
                tag.name,
                tag.commit.committed_datetime.strftime("%Y-%m-%d"),
                get_git_tag_url(
                    repo.git_cloud,
                    repo.sanitized_url,
                    tag.name,
                ),
            )
            for tag in source
        )
    )


def map_tag_csv_row_to_dict(row: GitTagCsvRow) -> dict[str, str]:
    """
    Maps tag csv row to dictionary
    """
    return {
        "component": row[0],
        "tag": row[1],
        "date": row[2],
        "url": row[3],
    }


def sort_tag_csv_rows_by_date(tags: list[GitTagCsvRow]) -> list[GitTagCsvRow]:
    """
    Sorts tags by date
    """
    return sorted(tags, key=lambda t: t[2])
