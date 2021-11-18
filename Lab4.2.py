import json
import yaml


def convert_json_to_yaml(input_file, output_file):
    """
    Function of conversion
    :param input_file: name of file get json from
    :param output_file: name of file to put yaml to
    :return: nothing
    """
    with open(input_file, 'r', encoding="UTF8") as input_file:
        data = json.load(input_file)
        with open(output_file, 'w', encoding="UTF8") as output_file:
            yaml.dump(data, output_file, allow_unicode=True)


convert_json_to_yaml("BeforeParsing.txt", "AfterParsing.txt")


# import time
# start_time = time.time()
# n = 10000
# for i in range(n):
#     convert_json_to_yaml("BeforeParsing.txt", "AfterParsing.txt")
# end_time = time.time()
# print(f"{n} loops, {(end_time - start_time) / n} per loop")
