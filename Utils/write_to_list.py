# write to list
import csv
import sys
from globals import fileName


def writeFileTitle(data_title: str, no_decoration = False):
    with open(fileName, 'a', encoding="utf-8") as file:
        writer = csv.writer(file)
        if no_decoration:
            writer.writerow([data_title])
        else:
            writer.writerow([f'=== {data_title} ==='])


def writeFileData(data_list: list, targetNumWeek: int):
    with open(fileName, 'a', encoding="utf-8") as file:
        writer = csv.writer(file)

        if not data_list or len(data_list) == 0:
            writer.writerow([f'No articles/blogs were found within {targetNumWeek} weeks'])
        else:
            for data in data_list:
                writer.writerow(data)

        # blank separator
        writer.writerow([])


def writeScrapedData(data_title: str, file, data_list: list, target_weeks):
    # print(data_list)
    # print(data_title)

    with open(file, 'a', encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([f'=== {data_title} ==='])
        if not data_list or len(data_list) == 0:
            writer.writerow([f'No articles/blogs were found within {target_weeks} weeks'])
        else:
            for data in data_list:
                writer.writerow(data)

        # blank separator
        writer.writerow([])
