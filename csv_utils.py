"""
Csv utilities
"""

import csv
import os

DEFAULT_CSV_DIRECTORY = "artifacts"
DEFAULT_CSV_OUTPUT = "packages-output.csv"


def export_packages_to_csv(
    data: list[dict[str, str]],
    path: str = DEFAULT_CSV_DIRECTORY,
    file_name: str = DEFAULT_CSV_OUTPUT,
) -> str:
    """
    Export data to csv file

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
        fieldnames = ["package", "tag", "date", "url"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

    return file_path
