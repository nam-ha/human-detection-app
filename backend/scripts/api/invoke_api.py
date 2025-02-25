import os
import sys

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
)

import json
import requests

from PIL import Image
from source.utils.image import pilimage_to_b64image, b64image_to_pilimage

from configs.general import env_config, paths_config

def main():
    # Load config
    config_file = os.path.join(
        paths_config.configs_folder,
        'script',
        'invoke_api_config.json'
    )
    
    with open(config_file, 'r') as file:
        config = json.load(file)
    
    # Load image
    pilimage = Image.open(
        fp = config.get('image_file')
    )
    
    b64image = pilimage_to_b64image(pilimage)
    
    # Predict
    response = requests.post(
        url = f'http://localhost:{env_config.port}/api/v1/predict',
        json = {
            'b64image': b64image,
            'confidence_threshold': config.get('confidence_threshold')
        }
    )
    
    b64image = response.json().get('b64image')
    num_humans = response.json().get('num_humans')
    
    print("Num detected people: ", num_humans)
    
    pilimage = b64image_to_pilimage(b64image)
    pilimage.show()


if __name__ == '__main__':
    main()
