"""
Csv utilities
"""

import csv

DEFAULT_CSV_OUTPUT = "packages-output.csv"


def export_packages_to_csv(data, file_name: str = DEFAULT_CSV_OUTPUT):
    """Export data to csv file"""
    if file_name is None:
        file_name = DEFAULT_CSV_OUTPUT

    with open(file_name, "w", newline="", encoding="utf-8") as csv_file:
        fieldnames = ["package", "tag", "date", "url"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
