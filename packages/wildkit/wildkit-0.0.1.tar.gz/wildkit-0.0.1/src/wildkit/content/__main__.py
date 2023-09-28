import argparse
import sys
import dataclasses
import time

import src.wildkit.common as common
import src.wildkit.content as content


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-t', '--token', help='API token')
    env = arg_parser.parse_args()

    if not env.token:
        raise Exception("token is missing")

    ses = common.new_client(env.token)
    #categories = content.configurator_get_all_categories(ses)
    #print(categories)

    characteristics = content.configurator_get_all_characteristics(ses, "Косухи")
    print(characteristics)

    colors = content.configurator_get_all_colors(ses)
    print(colors)
    colors_tree = content.tree([dataclasses.asdict(c) for c in colors], "name", "parentName", "_children")
    content.print_tree(colors_tree, "_children", lambda x: x["name"])

    genders = content.configurator_get_all_genders(ses)
    print(genders)

    countries = content.configurator_get_all_countries(ses)
    print(countries)

    seasons = content.configurator_get_all_seasons(ses)
    print(seasons)

    tnveds = content.configurator_get_all_tnveds(ses, "Блузки")
    print(tnveds)

    #barcodes = wildkit.content.generate_barcodes(ses, 2)
    #print(barcodes)

    limits = content.get_limits(ses)
    print(limits)

    size = content.CreateCardSize(techSize="42", wbSize="43", price=100, skus=["12345"])
    properties = [
        content.new_property_subject("Платья")
    ]
    card = content.CreateCard(characteristics=properties, vendorCode="test", sizes=[size])
    content.create_cards(ses, [card])
    time.sleep(1.0)
    errors = content.get_errors(ses)
    if errors:
        print(errors)
    print(content.get_all_cards(ses))


if __name__ == '__main__':
    sys.exit(main())
