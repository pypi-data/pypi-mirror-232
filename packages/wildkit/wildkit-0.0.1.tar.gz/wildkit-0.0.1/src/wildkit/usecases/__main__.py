import argparse
import sys

import src.wildkit.common as common
import src.wildkit.content as content


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-t', '--token', help='API token')
    env = arg_parser.parse_args()

    if not env.token:
        raise Exception("token is missing")

    ses = common.new_client(env.token)
    categories = content.configurator_get_all_categories(ses)
    print(categories)


if __name__ == '__main__':
    sys.exit(main())
