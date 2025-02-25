import os

import uvicorn
import base64

from fastapi import FastAPI, APIRouter, Depends, HTTPException

from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, Field, field_validator

from io import BytesIO
from PIL import Image
from datetime import datetime
from typing import List

from source.core import HumanDetector
from source.modules.database import HumanDetectorDatabase, Predictions
from source.utils.image import BBoxDrawer, save_b64image, strip_mime_prefix

from configs.general import env_config, paths_config
    
def setup_folders():
    os.makedirs(
        paths_config.media_storage_folder,
        exist_ok = True
    )
     
# ==

# Setup database
database = HumanDetectorDatabase(
    database_url = env_config.database_url
)

database.create_tables()

# Init model
detector = HumanDetector()

detector.load_model(
    model_file = os.path.join(
        paths_config.models_folder,
        'finetuned',
        env_config.model_filename
    )
)

bbox_drawer = BBoxDrawer()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

router = APIRouter(prefix = "/api/v1")

class PredictRequest(BaseModel):
    b64image: str
    confidence_threshold: float = Field(ge = 0.0, le = 1.0)

    @field_validator("b64image")
    @classmethod
    def validate_b64image(cls, b64image):
        b64image = strip_mime_prefix(b64image)
    
        try:
            image_data = base64.b64decode(b64image)
            
            image_buffer = BytesIO(image_data)
            
            pilimage = Image.open(image_buffer)
            
            pilimage.verify()
            
        except Exception:
            raise ValueError("Invalid base64 image data.")
        
        pilimage_size = pilimage.size[0] * pilimage.size[1]
        
        if pilimage_size < env_config.min_image_size:
            raise ValueError("Image too small.")
        
        if pilimage_size > env_config.max_image_size:
            raise ValueError("Image too large.")
        
        format = pilimage.format
        if format not in ['PNG', 'JPEG', 'JPG']:
            raise ValueError(f"Not supported image format: {format}")
            
        return b64image
        
class PredictResponse(BaseModel):
    b64image: str
    num_humans: int
    
@router.post("/predict")
async def predict(request: PredictRequest) -> PredictResponse:
    current_time = datetime.now()
    current_time_str = current_time.strftime("%Y-%m-%d_%H-%M-%S")
            
    query_image_file = os.path.join(
        paths_config.media_storage_folder,
        'queries',
        f'{current_time_str}.png'
    )
    
    result_image_file = os.path.join(
        paths_config.media_storage_folder,
        'results',
        f'{current_time_str}.png'
    )
        
    predictions = detector.predict_b64image(
        b64image = request.b64image,
        confidence_threshold = request.confidence_threshold
    )
    
    prediction = predictions[0]
    
    xywhs = prediction.boxes.xywh.tolist()
    classes = prediction.boxes.cls.tolist()
    confidences = prediction.boxes.conf.tolist()
    
    num_detected_objects = len(xywhs)
        
    drawn_b64image = bbox_drawer.draw_bboxes_on_b64image(
        b64image = request.b64image,
        xywhs = xywhs,
        labels = ['human' for _ in range(len(xywhs))],
        confidences = confidences,
        colors = ['red' for _ in range(len(xywhs))],
        line_width = 2
    )
    
    save_b64image(
        b64image = request.b64image,
        save_file = query_image_file
    )
    
    save_b64image(
        b64image = drawn_b64image, 
        save_file = result_image_file
    )
    
    prediction_record = Predictions(
        time = current_time,
        query_image_file = query_image_file,
        result_image_file = result_image_file,
        num_humans = num_detected_objects
    )
    
    database.add_record(prediction_record)
    
    return PredictResponse(
        b64image = drawn_b64image,
        num_humans = num_detected_objects
    )


class HistoryRequest(BaseModel):
    page_index: int = Field(ge = 1, default = 1)
    page_size: int = Field(ge = 1, default = 10)
    
    query_id: str | None = None
    
    time_min: str | None = None
    time_max: str | None = None

    num_humans_min: str | None = None
    num_humans_max: str | None = None
    
    @field_validator("query_id")
    @classmethod
    def validate_query_id(cls, query_id):
        if query_id is not None and query_id != "":
            try:
                _ = int(query_id)
                
            except Exception:
                raise HTTPException(
                    422, 
                    detail = [
                        {
                            'msg': "Invalid query id. Must be an integer.",
                        }
                    ]
                )
                
        return query_id
    
    @field_validator("time_min")
    @classmethod
    def validate_time_min(cls, time_min):
        if time_min is not None and time_min != "":
            try:
                _ = datetime.strptime(time_min, "%Y-%m-%d_%H-%M-%S")
                
            except Exception:
                raise HTTPException(
                    422, 
                    detail = [
                        {
                            'msg': "Invalid time format. Must be in the format: YYYY-MM-DD_HH-MM-SS",
                        }
                    ]
                )
            
        return time_min
    
    @field_validator("time_max")
    @classmethod
    def validate_time_max(cls, time_max):
        if time_max is not None and time_max != "":
            try:
                _ = datetime.strptime(time_max, "%Y-%m-%d_%H-%M-%S")
                
            except Exception:
                raise HTTPException(
                    422, 
                    detail = [
                        {
                            'msg': "Invalid time format. Must be in the format: YYYY-MM-DD_HH-MM-SS",
                        }
                    ]
                )
            
        return time_max

    @field_validator("num_humans_min")
    @classmethod
    def validate_num_humans_min(cls, num_humans_min):
        if num_humans_min is not None and num_humans_min != "":
            try:
                int(num_humans_min)
                
            except Exception:
                raise HTTPException(
                    422, 
                    detail = [
                        {
                            'msg': "Invalid number of humans. Must be an integer.",
                        }
                    ]
                )

        return num_humans_min
    
    @field_validator("num_humans_max")
    @classmethod
    def validate_num_humans_max(cls, num_humans_max):
        if num_humans_max is not None and num_humans_max != "":
            try:
                int(num_humans_max)
                
            except Exception:
                raise HTTPException(
                    422, 
                    detail = [
                        {
                            'msg': "Invalid number of humans. Must be an integer.",
                        }
                    ]
                )
            
        return num_humans_max
    
class HistoryRecord(BaseModel):
    query_id: int
    time: str
    
    query_image_file: str
    result_image_file: str
    num_humans: int

class HistoryResponse(BaseModel):
    total: int
    
    records: List[HistoryRecord]
    
@router.get("/history")
async def get_history(
    request: HistoryRequest = Depends()
) -> HistoryResponse:
    records, total = database.get_records_from_predictions(
        query_id = request.query_id,
        time_min = request.time_min,
        time_max = request.time_max,
        num_humans_min = request.num_humans_min,
        num_humans_max = request.num_humans_max,
        page_size = request.page_size,
        page_index = request.page_index
    )
    
    return HistoryResponse(
        total = total,
        
        records = [
            HistoryRecord(
                query_id = record.query_id,
                time = record.time.strftime("%Y-%m-%d_%H-%M-%S"),
                query_image_file = record.query_image_file,
                result_image_file = record.result_image_file,
                num_humans = record.num_humans
            )
            for record in records
        ]
    )

app.include_router(router)

def main(): 
    setup_folders()
    
    uvicorn.run(
        app, 
        host = "0.0.0.0", 
        port = env_config.port
    )
    
if __name__ == '__main__':
    main()
