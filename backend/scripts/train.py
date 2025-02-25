import os
import sys

sys.path.append(
    os.path.dirname(os.path.dirname(__file__))
)

import json

from source.core import HumanDetector

from configs.general import env_config, paths_config

def main():
    # Load config
    config_file = os.path.join(
        paths_config.configs_folder,
        'script',
        'train_config.json'
    )
    
    with open(config_file, 'r') as file:
        config = json.load(file)
        
    # Init model
    detector = HumanDetector()
    
    # Train model
    detector.train(
        base_model = config.get('base_model'),
        
        dataset_config_file = os.path.join(
            paths_config.datasets_folder,
            config.get('dataset_name'),
            'data.yaml'
        ),
        
        num_epochs = config.get('num_epochs'),
        image_size = config.get('image_size'),
    )
    
    
if __name__ == '__main__':
    main()
