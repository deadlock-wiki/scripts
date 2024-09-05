import pandas as pd

OUTPUT_DIR = '../output-data'


def export_json_file_to_csv(file_name, columns_ordering):
    df = pd.read_json(f'{OUTPUT_DIR}/json/{file_name}.json').transpose()
    df = df.applymap(convert_array_to_string)
    rest_of_columns = []
    for column in df.columns:
        if column not in columns_ordering:
            rest_of_columns.append(column)

    df = df[columns_ordering + rest_of_columns]
    df.to_csv(f'{OUTPUT_DIR}/csv/{file_name}.csv')


def convert_array_to_string(value):
    if isinstance(value, list):
        return ', '.join(value)
    return value


if __name__ == '__main__':
    export_json_file_to_csv(
        'item-data',
        [
            'Name',
            'Description',
            'Cost',
            'Tier',
            'Activation',
            'Slot',
            'Components',
            'TargetTypes',
            'ShopFilters',
        ],
    )
    export_json_file_to_csv(
        'hero-data',
        [
            'Name',
            'Dps',
            'BulletDamage',
            'ClipSize',
            'BulletsPerSec',
            'LightMeleeDamage',
            'HeavyMeleeDamage',
            'MaxHealth',
            'HealthRegen',
            'MaxMoveSpeed',
            'SprintSpeed',
            'Stamina',
            'LevelScaling',
        ],
    )
