import os
import sys

sys.path.append(
    os.path.dirname(os.path.dirname(__file__))
)

from ultralytics import YOLO

from source.utils.image import b64image_to_pilimage

class HumanDetector():
    def __init__(self):
        pass
    
    def load_model(self, model_file):
        self._model = YOLO(model_file)
    
    def train(self,
              base_model,
              dataset_config_file,
              num_epochs,
              image_size
    ):
        self._model = YOLO(base_model)
        self._trained_image_size = image_size
        
        self._model.train(
            data = dataset_config_file,
            epochs = num_epochs,
            imgsz = image_size,
            
            optimizer = 'AdamW',
            patience = 2
        )
    
    def predict_b64image(self, b64image, confidence_threshold):
        if self._model:
            pilimage = b64image_to_pilimage(b64image)
            
            predictions = self._model.predict(
                source = pilimage, 
                imgsz = 640, 
                conf = confidence_threshold
            )
            
            return predictions
        
        else:
            print("No model selected ...") 
            
    def predict_from_file(self, image_file, confidence_threshold):
        if self._model:            
            predictions = self._model.predict(
                source = image_file, 
                imgsz = 640, 
                conf = confidence_threshold
            )
            
            return predictions
        
        else:
            print("No model selected ...") 
