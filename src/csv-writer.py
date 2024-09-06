import pandas as pd
from utils import json_utils

OUTPUT_DIR = '../output-data'


def export_json_file_to_csv(file_name, columns_ordering):
    data = json_utils.read(f'{OUTPUT_DIR}/json/{file_name}.json')

    main_columns = [x[0] for x in columns_ordering]

    data = {key: filter_data(data[key], main_columns) for key in data}
    data = [flatten_data(data[key], columns_ordering) for key in data]

    df = pd.DataFrame(data)
    df = df.applymap(convert_array_to_string)

    rest_of_columns = []
    for column in df.columns:
        if column not in columns_ordering:
            rest_of_columns.append(column)

    df.columns = pd.MultiIndex.from_tuples(columns_ordering)

    df.to_csv(f'{OUTPUT_DIR}/csv/{file_name}.csv', index=False)


def filter_data(data, columns):
    filtered_data = {}
    for column in columns:
        if column in data:
            filtered_data[column] = data[column]

    return filtered_data


def convert_array_to_string(value):
    if isinstance(value, list):
        return ', '.join(value)
    return value


def flatten_data(data, column_tuples):
    flat_data = {}
    for column_tuple in column_tuples:
        key = ''
        value = data

        for column in column_tuple:
            if column == '':
                continue

            key += column
            if column in value:
                value = value[column]

        # do not assign objects to column values
        if isinstance(value, dict):
            flat_data[key] = ''
        else:
            flat_data[key] = value

    return flat_data


if __name__ == '__main__':
    export_json_file_to_csv(
        'item-data',
        [
            ['Name'],
            ['Description'],
            ['Cost'],
            ['Tier'],
            ['Activation'],
            ['Slot'],
            ['Components'],
            ['TargetTypes'],
            ['ShopFilters'],
        ],
    )

    export_json_file_to_csv(
        'hero-data',
        [
            ['Name', '', ''],
            ['Dps', '', ''],
            ['BulletDamage', '', ''],
            ['ClipSize', '', ''],
            ['BulletsPerSec', '', ''],
            ['LightMeleeDamage', '', ''],
            ['HeavyMeleeDamage', '', ''],
            ['MaxHealth', '', ''],
            ['HealthRegen', '', ''],
            ['MaxMoveSpeed', '', ''],
            ['SprintSpeed', '', ''],
            ['Stamina', '', ''],
            ['LevelScaling', 'BulletDamage', ''],
            ['LevelScaling', 'MeleeDamage', ''],
            ['LevelScaling', 'Health', ''],
            ['LevelScaling', 'TechDamagePerc', ''],
            ['LevelScaling', 'BulletResist', ''],
            ['LevelScaling', 'BonusAttackRange', ''],
            ['BoundAbilities', '1', 'Name'],
            ['BoundAbilities', '2', 'Name'],
            ['BoundAbilities', '3', 'Name'],
            ['BoundAbilities', '4', 'Name'],
        ],
    )
