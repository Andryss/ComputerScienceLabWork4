import re


class Node:
    """
    Class for creating tree with tokens
    :param parent: link to the parent node
    :param data: content of the node (dict or array)
    """
    parent = None
    data = None

    def __init__(self, parent):
        self.parent = parent


def convert_json_to_yaml(input_file, output_file):
    """
    Main function of conversion
    :param input_file: name of file get json from
    :param output_file: name of file to put yaml to
    :return: nothing
    """
    input_text = open(input_file, encoding="UTF8").read()
    output_text = converter(input_text)
    output_file = open(output_file, 'w', encoding="UTF8")
    output_file.write(output_text)


def converter(text):
    """
    Function with all process we need to do with json text
    :param text: json-format text
    :return: yaml-format text
    """
    sequence = check_and_tokenize(text)
    root = create_tree(sequence)
    text = write_object(root.data["root"].data, 0)
    return text


def write_object(dictionary: dict, spaces: int, first_no_space=False):
    """
    Function which writes the yaml object according to node's dict (object)
    :param dictionary: node's dict with key-values (or empty)
    :param spaces: number of spaces to save form of the yaml text
    :param first_no_space: special option which mark if first line doesn't need start spaces (especially for arrays)
    :return: string of the yaml object
    """
    string = ""
    if len(dictionary) == 0:
        return " {}\n"
    for key in list(dictionary.keys()):
        if first_no_space:
            string += key + ":"
            first_no_space = False
        else:
            string += spaces * " " + key + ":"
        value = dictionary[key]
        if isinstance(value, Node):
            if len(value.data) == 0:
                string += write_object(value.data, spaces)
            elif isinstance(value.data, dict):
                string += "\n"
                string += write_object(value.data, spaces + 4)
            elif isinstance(value.data, list):
                string += "\n"
                string += write_array(value.data, spaces + 2)
        else:
            if len(value) == 0:
                value = '""'
            string += " " + value + "\n"
    return string


def write_array(array: list, spaces: int, first_no_spaces=False):
    """
    Function which writes the yaml array according to node's list
    :param array: node's list with values
    :param spaces: number of spaces to save form of the yaml text
    :param first_no_spaces: special option which mark if first line doesn't need start spaces (especially for arrays)
    :return: string of the yaml array
    """
    string = ""
    if len(array) == 0:
        return " []\n"
    for value in array:
        if first_no_spaces:
            string += "- "
            first_no_spaces = False
        else:
            string += spaces * " " + "- "
        if isinstance(value, Node):
            if len(value.data) == 0:
                string += write_object(value.data, spaces)
            elif isinstance(value.data, dict):
                string += write_object(value.data, spaces + 2, first_no_space=True)
            elif isinstance(value.data, list):
                string += write_array(value.data, spaces + 2, first_no_spaces=True)
        else:
            if len(value) == 0:
                value = '""'
            string += value + "\n"
    return string


def create_tree(sequence):
    """
    Function which transforms sequence with tokens into abstract tree
    :param sequence: sequence with tokens
    :return: node root of the abstract tree
    """
    current_node = Node(None)
    current_node.data = {}

    for index, element in enumerate(sequence):

        if element.startswith("\"") or element in ["true", "false", "null"]:
            if element.startswith("\""):
                element = element[1:-1]
            if sequence[index - 1] == ":":
                current_node.data[sequence[index - 2][1:-1]] = element
            elif sequence[index + 1] == ":":
                current_node.data[element] = None
            else:
                current_node.data.append(element)

        elif element == "{":
            if sequence[index - 1] == ":":
                current_node.data[sequence[index - 2][1:-1]] = Node(current_node)
                current_node = current_node.data[sequence[index - 2][1:-1]]
            else:
                current_node = Node(current_node)
                current_node.parent.data.append(current_node)
            current_node.data = {}

        elif element == "}":
            current_node = current_node.parent

        elif element == "[":
            if sequence[index - 1] == ":":
                current_node.data[sequence[index - 2][1:-1]] = Node(current_node)
                current_node = current_node.data[sequence[index - 2][1:-1]]
            else:
                current_node = Node(current_node)
                current_node.parent.data.append(current_node)
            current_node.data = []

        elif element == "]":
            current_node = current_node.parent

        elif element[0].isdigit():
            if sequence[index - 1] == ":":
                current_node.data[sequence[index - 2][1:-1]] = element
            else:
                current_node.data.append(element)

    while current_node.parent:
        current_node = current_node.parent

    return current_node


def check_and_tokenize(json):
    """
    Function which finds usual mistakes and slices json into tokens
    :param json: json-format text
    :return: sequence with tokens
    """
    sequence = ["\"root\"", ":"]

    operands = []
    value = ["string", "number", "object", "array"]
    flags = value.copy()

    string = re.compile(r"\".*?\"")
    number = re.compile(r"(\d|\.)+")

    index = 0
    while index < len(json):
        symbol = json[index]

        if symbol == "\"":
            assert "string" in flags, f"{json[index - 2:index + 3]} неправильный формат json"
            result = string.match(json[index:])

            sequence.append(result.group())
            flags = [":", "]", "}", ","]
            index += result.span()[1] - 1

        elif symbol == "{":
            assert "object" in flags, f"{json[index - 2:index + 3]} неправильный формат json"
            flags = ["string", "}"]
            operands.append(symbol)

            sequence.append(symbol)

        elif symbol == "}":
            assert operands[-1] == "{", f"{json[index - 2:index + 3]} неправильный формат json"
            assert "}" in flags, f"{json[index - 2:index + 3]} неправильный формат json"
            del operands[-1]
            flags = [",", "}", "]"]

            sequence.append(symbol)

        elif symbol == "[":
            flags = ["]"] + value
            operands.append(symbol)

            sequence.append(symbol)

        elif symbol == "]":
            assert operands[-1] == "[", f"'{json[index - 2:index + 3]}' неправильный формат json"
            assert "]" in flags, f"'{json[index - 2:index + 3]}' неправильный формат json"
            del operands[-1]
            flags = [",", "}", "]"]

            sequence.append(symbol)

        elif symbol == ":":
            assert ":" in flags, f"'{json[index - 2:index + 3]}' неправильный формат json"
            flags = value.copy()

            sequence.append(symbol)

        elif symbol.isdigit():
            assert "number" in flags, f"'{json[index - 2:index + 3]}' неправильный формат json"
            result = number.match(json[index:])

            sequence.append(result.group())
            flags = [",", "}", "]"]
            index += result.span()[1] - 1

        elif symbol == "t":
            assert json[index: index + 4] == "true", f"'{json[index - 2:index + 3]}' неправильный формат json"
            assert "number" in flags, f"'{json[index - 2:index + 3]}' неправильный формат json"
            flags = [",", "}", "]"]
            index += 3

            sequence.append("true")

        elif symbol == "f":
            assert json[index: index + 5] == "false", f"'{json[index - 2:index + 3]}' неправильный формат json"
            assert "number" in flags, f"'{json[index - 2:index + 3]}' неправильный формат json"
            flags = [",", "}", "]"]
            index += 4

            sequence.append("false")

        elif symbol == "n":
            assert json[index: index + 4] == "null", f"'{json[index - 2:index + 3]}' неправильный формат json"
            assert "number" in flags, f"'{json[index - 2:index + 3]}' неправильный формат json"
            flags = [",", "}", "]"]
            index += 3

            sequence.append("null")

        elif symbol == ",":
            assert "," in flags, f"'{json[index - 2:index + 3]}' неправильный формат json"
            assert operands[-1] in ["{", "["], f"'{json[index - 2:index + 3]}' неправильный формат json"
            flags = value.copy()

            sequence.append(symbol)

        index += 1

    return sequence


convert_json_to_yaml("BeforeParsing.txt", "AfterParsing.txt")


import time
start_time = time.time()
n = 10000
for i in range(n):
    convert_json_to_yaml("BeforeParsing.txt", "AfterParsing.txt")
end_time = time.time()
print(f"{n} loops, {(end_time - start_time) / n} per loop")
