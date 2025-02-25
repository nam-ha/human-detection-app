import os
import sys

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
)

import json
import requests

from configs.general import env_config, paths_config

def main():
    # Load config
    config_file = os.path.join(
        paths_config.configs_folder,
        'script', 'api', 'invoke_history_config.json'
    )
    
    with open(config_file, 'r') as file:
        config = json.load(file)
        
    # Predict
    breakpoint()
    parametrized_url = f'http://localhost:{env_config.port}/api/v1/history?'
    if 'search_query_id' in config:
        parametrized_url += f'search_query_id={config["search_query_id"]}&'
        
    if 'time_min' in config:
        parametrized_url += f'time_min={config["time_min"]}&'
        
    if 'time_max' in config:
        parametrized_url += f'time_max={config["time_max"]}&'
    
    if 'num_humans_min' in config:
        parametrized_url += f'num_humans_min={config["num_humans_min"]}&'
        
    if 'num_humans_max' in config:
        parametrized_url += f'num_humans_max={config["num_humans_max"]}&'
    
    if 'page_size' in config:
        parametrized_url += f'page_size={config["page_size"]}&'
        
    if 'page_index' in config:
        parametrized_url += f'page_index={config["page_index"]}&'
    
    response = requests.get(
        url = parametrized_url
    )
    
    records = response.json().get('records')
    total = response.json().get('total')
    
    print("Records: ", records)
    print("Total: ", total)


if __name__ == '__main__':
    main()
