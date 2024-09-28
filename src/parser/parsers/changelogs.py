import sys
import os
from os import listdir
from os.path import isfile, join
import datetime

# bring utils module in scope
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils.json_utils as json_utils

from .constants import OUTPUT_DIR


class ChangelogParser:
    def __init__(self):
        self.CHANGELOGS_DIR = os.path.join(os.path.dirname(__file__), '../raw-changelogs/')
        self.OUTPUT_DIR = OUTPUT_DIR
        self.OUTPUT_CHANGELOGS = self.OUTPUT_DIR + '/changelogs'
        self.resources = self._get_resources()

    def run_all(self):
        changelogs_by_date = {}
        files = [f for f in listdir(self.CHANGELOGS_DIR) if isfile(join(self.CHANGELOGS_DIR, f))]
        for file in files:
            date = file.replace('.txt', '')
            changelog = self.run(date)
            changelogs_by_date[date] = changelog

        # take parsed changelogs and transform them into some other useful formats
        # self._create_resource_changelogs(changelogs_by_date)
        # self._create_changelog_db_data(changelogs_by_date)

    def run(self, version):
        logs = self._read_logs(version)
        changelog_lines = logs.split('\n')

        current_heading = 'Other'
        default_category = 'General'
        changelog_dict = {
            current_heading: [],
            'Heroes': [],
            'Items': [],
            'Abilities': [],
        }

        for line in changelog_lines:
            if line is None or line == '':
                continue

            # if heading is found, update current heading
            if line.startswith('[ '):
                current_heading = line[2:-2]
                current_heading = current_heading.replace(
                    ' Changes', ''
                )  # i.e. 'Map Changes' > 'Map'
                changelog_dict[current_heading] = []
                continue

            # find if a resource can be assigned a changelog line
            resource_tags = []
            group = current_heading
            for resource_key in self.resources:
                resource = self.resources[resource_key]
                resource_type = resource['Type']
                resource_name = resource['Name']

                if resource_type == 'Abilities':
                    continue  # skip abilities for now, may change format later

                if resource_name is None:
                    continue

                # Determine if the line is about this resource
                # resource (i.e. hero) name in english is found in the line
                if resource_name in line:
                    resource_tags.append(resource_name)

                    # If its a Hero, check if any of their 4 abilities are mentioned
                    if resource_type == 'Heroes':
                        if 'BoundAbilities' not in resource:
                            continue
                        for index, ability in resource['BoundAbilities'].items():
                            ability_key = ability['Key']
                            ability_name = ability['Name']
                            if ability_name is None:
                                continue

                            # ability name in english is found in the line
                            if ability_name in line:
                                include_tag = True
                                resource_tags.append(ability_name)
                                break

            # if no resource is found, assign to default group
            if len(resource_tags) == 0:
                resource_tags.append(default_category)

            for tag in resource_tags:
                # strip redundant prefix as it is already grouped under resource_name
                if line.startswith(f'- {tag}: '):
                    line = line.replace(f'{tag}: ', '')

            changelog_dict[group].append({'Description': line, 'Tags': resource_tags})

        changelog_with_icons = changelog_dict
        # changelog_with_icons = self._embed_icons(changelog_dict)

        json_utils.write(self.OUTPUT_CHANGELOGS + f'/date/{version}.json', changelog_with_icons)
        return changelog_with_icons

    # "Icon" is appended to i.e. "Hero" to make the template, "HeroIcon"
    resource_type_to_template_map = {'Heroes': 'Hero', 'Items': 'Item', 'Abilities': 'Ability'}

    # mass find and replace of any resource names with the ability icon template
    def _embed_icons(self, changelog):
        new_changelog = changelog.copy()

        for header, log_groups in changelog.items():
            for group_name, logs in log_groups.items():
                for index, log in enumerate(logs):
                    for resource_key in self.resources:
                        resource = self.resources[resource_key]
                        resource_name = resource['Name']
                        if resource_name is None:
                            continue

                        # Check if the resource's english name
                        # or key is referenced in the log
                        # english name matching: i.e.
                        # "Essence Bomb" and "Essence Bomb"
                        # key matching: i.e. "Blood Bomb" in log;
                        # "ability_blood_bomb" is the resource key,
                        # "Essence Bomb" is the english name
                        # this captures it being referenced
                        resource_found = False
                        if resource_name in log:
                            resource_found = True

                        if not resource_found:
                            # Lady Geist Blood Bomb to ladygeistbloodbomb
                            log_flattened = log.lower().replace(' ', '')

                            # ability_blood_bomb to bloodbomb
                            resource_key_flattened = resource_key.replace('ability_', '').replace(
                                '_', ''
                            )

                            if resource_key_flattened in log_flattened:
                                # ability_blood_bomb to Blood Bomb
                                resource_name = (
                                    resource_key.replace('ability_', '').replace('_', ' ').title()
                                )
                                resource_found = True

                        if not resource_found:
                            continue

                        # Retrieve the resource's type
                        resource_type = resource['Type']
                        resource_type_singular = self.resource_type_to_template_map[resource_type]
                        # "Ability" type to "AbilityIcon" template
                        template = resource_type_singular + 'Icon'

                        icon = (
                            '{{'
                            + template
                            + '|'
                            + resource_type_singular
                            + '='
                            + resource_name
                            + '|Size=20}}'
                        )
                        log = log.replace(resource_name, f'{icon} {resource_name}')
                        new_changelog[header][group_name][index] = log

        return new_changelog

    def _read_logs(self, version):
        # files just
        f = open(self.CHANGELOGS_DIR + f'{version}.txt', 'r', encoding='utf8')
        return f.read()

    def _get_resources(self):
        resources = {}
        heroes = json_utils.read(self.OUTPUT_DIR + '/json/hero-data.json')
        items = json_utils.read(self.OUTPUT_DIR + '/json/item-data.json')
        abilities = json_utils.read(self.OUTPUT_DIR + '/json/ability-data.json')

        for key in heroes:
            heroes[key]['Type'] = 'Heroes'

        for key in items:
            items[key]['Type'] = 'Items'

        for key in abilities:
            abilities[key]['Type'] = 'Abilities'

        resources.update(heroes)
        resources.update(items)
        resources.update(abilities)

        return resources

    # Creates historic changelog for each resource (eg. heroes, items etc.)
    # using each parsed changelog
    def _create_resource_changelogs(self, changelogs_by_date):
        hero_changelogs = {}
        for date, changelog in changelogs_by_date.items():
            for hero, changes in changelog['Heroes'].items():
                if hero not in hero_changelogs:
                    hero_changelogs[hero] = {}
                hero_changelogs[hero][date] = changes

        for hero_name, changelog in hero_changelogs.items():
            json_utils.write(
                self.OUTPUT_CHANGELOGS + f'/hero/{hero_name}.json',
                self._sort_object_by_date_key(changelog),
            )

        item_changelogs = {}
        for date, changelog in changelogs_by_date.items():
            for item, changes in changelog['Items'].items():
                if item not in item_changelogs:
                    item_changelogs[item] = {}
                item_changelogs[item][date] = changes

        for item_name, changelog in item_changelogs.items():
            json_utils.write(
                self.OUTPUT_CHANGELOGS + f'/item/{item_name}.json',
                self._sort_object_by_date_key(changelog),
            )

    # Convert changelogs to an array of rows, with the plan to upload
    # them to a database (TODO)
    def _create_changelog_db_data(self, changelogs):
        rows = []
        for date, changelog in changelogs.items():
            for header, log_groups in changelog.items():
                for group_name, logs in log_groups.items():
                    for index, log in enumerate(logs):
                        changelog_row = {
                            'id': f'{header}-{group_name}-{index}',
                            'changelog': log,
                            'resource_key': group_name,
                            'resource_type': header,
                            'patch_version': '',
                            'timestamp': date,
                        }
                        rows.append(changelog_row)

        return rows

    def _sort_object_by_date_key(self, changelogs):
        sorted_keys = sorted(
            changelogs.keys(), key=lambda x: datetime.datetime.strptime(x, '%m-%d-%Y')
        )

        sorted_changelogs = {}
        for key in reversed(sorted_keys):
            sorted_changelogs[key] = changelogs[key]

        return sorted_changelogs


if __name__ == '__main__':
    ChangelogParser().run_all()
