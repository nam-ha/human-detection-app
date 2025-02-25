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
        'predict_config.json'
    )
    
    with open(config_file, 'r') as file:
        config = json.load(file)
        
    # Init model
    detector = HumanDetector()
    
    detector.load_model(
        model_file = os.path.join(
            paths_config.models_folder,
            'finetuned',
            config.get('trained_model_filename')
        )
    )
    
    # Predict
    predictions = detector.predict_from_file(
        image_file = os.path.join(
            paths_config.datasets_folder,
            config.get('dataset_name'),
            'test',
            config.get('test_image_filename')
        ),
        
        confidence_threshold = 0.5
    )

    print(predictions)


if __name__ == '__main__':
    main()
