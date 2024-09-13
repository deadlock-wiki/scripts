import sys
import os

# bring utils module in scope
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from .constants import OUTPUT_DIR
import utils.json_utils as json_utils
import utils.string_utils as string_utils


class AbilityParser:
    def __init__(self, abilities_data, localizations):
        self.abilities_data = abilities_data
        self.localizations = localizations

    def run(self):
        all_abilities = {}

        for ability_key in self.abilities_data:
            ability = self.abilities_data[ability_key]
            if type(ability) is not dict:
                continue

            if 'm_eAbilityType' not in ability:
                continue

            if ability['m_eAbilityType'] not in ['EAbilityType_Signature', 'EAbilityType_Ultimate']:
                continue

            ability_data = {
                'Name': self.localizations['heroes'].get(ability_key, None),
            }

            stats = ability['m_mapAbilityProperties']
            for key in stats:
                stat = stats[key]

                value = None

                if 'm_strValue' in stat:
                    value = stat['m_strValue']

                elif 'm_strVAlue' in stat:
                    value = stat['m_strVAlue']

                ability_data[key] = value

            if 'm_vecAbilityUpgrades' not in ability:
                # print(ability.get('Name'), 'missing upgrades')
                continue
            else:
                ability_data['Upgrades'] = self.parse_upgrades(
                    ability_key, ability['m_vecAbilityUpgrades']
                )

            description = (self.localizations['heroes'].get(ability_key + '_desc'),)
            ability_data['Description'] = string_utils.format_description(description, ability_data)

            formatted_ability_data = {}
            for attr_key, attr_value in ability_data.items():
                # strip attrs with value of 0, as that just means it is irrelevant
                if attr_value != '0':
                    formatted_ability_data[attr_key] = string_utils.string_to_number(attr_value)

            all_abilities[ability_key] = json_utils.sort_dict(formatted_ability_data)

        json_utils.write(OUTPUT_DIR + 'json/ability-data.json', json_utils.sort_dict(all_abilities))

        return all_abilities

    def parse_upgrades(self, ability_key, upgrade_sets):
        parsed_upgrade_sets = []
        for index, upgrade_set in enumerate(upgrade_sets):
            parsed_upgrade_set = {'Description': None}
            # add and format the description of the ability upgrade
            desc_key = f'{ability_key}_t{index}_desc'
            print(desc_key)
            if desc_key in self.localizations:
                parsed_upgrade_set['Description'] = self.localizations[desc_key]

            for upgrade in upgrade_set['m_vecPropertyUpgrades']:
                parsed_upgrade_set[upgrade['m_strPropertyName']] = string_utils.string_to_number(
                    upgrade['m_strBonus']
                )

            parsed_upgrade_sets.append(parsed_upgrade_set)

        return parsed_upgrade_sets
