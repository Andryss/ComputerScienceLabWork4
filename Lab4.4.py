import json
import csv


def convert_json_to_csv(input_file, output_file):
    """
    Function of conversion
    :param input_file: name of file get json from
    :param output_file: name of file to put yaml to
    :return: nothing
    """
    with open(input_file, 'r', encoding="UTF8") as input_file:
        data = json.load(input_file)

        columns = ["day", "time", "room", "lesson", "lesson-format"]
        rows = []

        for row in data["tbody"]:
            row_tuple = ["" for i in columns]
            for field in list(row.keys()):
                field_index = columns.index(field)
                if isinstance(row[field], dict):
                    row_tuple[field_index] = "\n".join(list(row[field].values()))
                else:
                    row_tuple[field_index] = row[field]
            rows.append(row_tuple)

        with open(output_file, 'wt', encoding="UTF8", newline="") as output_file:
            writer = csv.writer(output_file)
            writer.writerows([columns] + rows)


convert_json_to_csv("BeforeParsing.txt", "AfterParsing.csv")


# import time
# start_time = time.time()
# n = 10000
# for i in range(n):
#     convert_json_to_yaml("BeforeParsing.txt", "AfterParsing.txt")
# end_time = time.time()
# print(f"{n} loops, {(end_time - start_time) / n} per loop")
