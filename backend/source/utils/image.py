import os
import base64

from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

def b64image_to_pilimage(b64image):
    image_data = base64.b64decode(b64image)
    
    image_buffer = BytesIO(image_data)
    
    pilimage = Image.open(image_buffer)
    
    return pilimage

def pilimage_to_b64image(pilimage):
    image_buffer = BytesIO()
    pilimage.save(image_buffer, format = 'PNG')
    b64image = base64.b64encode(image_buffer.getvalue()).decode('utf-8')
    
    return b64image

def save_b64image(b64image, save_file):
    save_folder = os.path.dirname(save_file)
    
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
        
    image_data = base64.b64decode(b64image)
    
    image_buffer = BytesIO(image_data)
    
    pilimage = Image.open(image_buffer)
    
    pilimage.save(save_file, format = 'PNG')

def strip_mime_prefix(b64image):
    if b64image.startswith('data:image/'):
        comma_index = b64image.find(',')
        if comma_index != -1:
            return b64image[comma_index + 1:] 
    
    return b64image
    
class BBoxDrawer():
    def __init__(self):
        pass
    
    def draw_bboxes_on_b64image(self, b64image, xywhs, labels, colors, confidences, line_width = 2):
        if len(xywhs) == 0:
            return b64image
        
        pilimage = b64image_to_pilimage(b64image)
        draw = ImageDraw.Draw(pilimage)
        font = ImageFont.load_default(size = 20)
    
        for xywh, label, confidence, color in zip(xywhs, labels, confidences, colors):
            x, y, w, h = xywh

            x_min = x - w // 2
            y_min = y - h // 2
            x_max = x + w // 2
            y_max = y + h // 2
            
            draw.rectangle(
                xy = (x_min, y_min, x_max, y_max), 
                outline = color, 
                width = line_width
            )

            text = f"{confidence:.2f}"
            text_bbox = draw.textbbox(
                xy = (0, 0),
                text = text, 
                font = font
            )
            
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
        
            text_background = (x_min, y_min - text_height - 4, x_min + text_width, y_min)

            draw.rectangle(text_background, fill = color)
            
            draw.text(
                xy = (x_min, y_min - text_height - 4), 
                text = text, 
                fill = "white", 
                font = font
            )
                        
        drawn_b64image = pilimage_to_b64image(pilimage)
        
        return drawn_b64image
