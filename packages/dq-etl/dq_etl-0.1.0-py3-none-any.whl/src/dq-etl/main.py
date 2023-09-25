import argparse
import json
from plugin_registry import plugin_factory
from controller import ETLController

def main(args):
    # Load configurations from JSON files provided in arguments
    with open(args.source_config, 'r') as src_file:
        source_config = json.load(src_file)

    with open(args.destination_config, 'r') as dest_file:
        destination_config = json.load(dest_file)

    # Initialize source and destination plugins using the factory function
    source = plugin_factory(source_config.pop('plugin_name'), **source_config)
    destination = plugin_factory(destination_config.pop('plugin_name'), **destination_config)

    # Further processing...
    controller = ETLController(source, destination)
    controller.execute(source_config['table_name'], 'destination_table_name')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='ETL process from source to destination.')
    parser.add_argument('source_config', type=str, help='Path to source configuration JSON file.')
    parser.add_argument('destination_config', type=str, help='Path to destination configuration JSON file.')

    args = parser.parse_args()
    main(args)
