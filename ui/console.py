""" This module contains the console interaction with user """


def input_tag_name() -> str:
    """
    Input tag

    :return: tag name or None if user wants to quit
    """
    return input_value('new tag')


def input_value(value_name: str) -> str:
    """
    Input any non empty value or quit

    :param value_name: name of value
    :return: non empty value or None if user wants to quit
    """
    value = input(f'Enter [{value_name}] or just press [q] to quit: ')
    if value.lower() == 'q':
        return None
    if value is None or value.strip() == '':
        print('Value cannot be empty')
        return input_tag_name()
    return value


def choose_from_or_skip(options: list[str]) -> str:
    """
    Choose from list of options

    :param options: string list of options
    :return: selected option or None if user wants to skip selection
    """
    if not options or len(options) == 0:
        return None

    options_view = {}
    for index, item in enumerate(options):
        view_index = index + 1
        options_view[view_index] = item
        print(f'{view_index}: {item}')

    selection = input(
        "\nEnter position number from the list " +
        "or just press enter to skip selection: ")
    if selection is None or selection.strip() == '':
        return None

    if selection.isdigit():
        item_position = int(selection)
        if item_position in options_view:
            return options_view[item_position]
    return choose_from_or_skip(options)
