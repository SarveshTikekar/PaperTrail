import cv2
import numpy as np
import pytesseract
from PIL import Image
from django.conf import settings

def preprocess_image(image_path):
    """Basic image cleanup: Grayscale, Denoising, and Thresholding."""
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Image not found at {image_path}")
    
    # 1. Grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 2. Denoising
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    
    # 3. Thresholding (Adaptive)
    # Binary inverse thresholding with Otsu's method
    _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    
    return thresh

def extract_text_from_roi(image, x, y, w, h, lang='eng'):
    """Extract text from a specific region (ROI) with confidence."""
    roi = image[y:y+h, x:x+w]
    # Use image_to_data to get confidence
    data = pytesseract.image_to_data(roi, lang=lang, output_type=pytesseract.Output.DICT)
    
    text_results = []
    conf_results = []
    
    for i in range(len(data['text'])):
        if int(data['conf'][i]) > -1:
            text_results.append(data['text'][i])
            conf_results.append(data['conf'][i])
            
    full_text = " ".join(text_results).strip()
    avg_conf = sum(conf_results) / len(conf_results) if conf_results else 0
    
    return full_text, avg_conf

def process_pan_49a(image_path):
    """Placeholder logic for PAN 49A extraction based on ROIs."""
    # In a real scenario, coordinates (x, y, w, h) would be defined in a template
    # Here we simulate the extraction for specific fields
    processed_img = preprocess_image(image_path)
    
    # Dummy coordinates for demonstration
    # In practice, these are measured from the template
    results = {
        'full_name': extract_text_from_roi(processed_img, 100, 100, 500, 50),
        'dob': extract_text_from_roi(processed_img, 100, 200, 300, 50),
        'aadhaar': extract_text_from_roi(processed_img, 100, 300, 500, 50),
    }
    
    return results

def process_voter_id_6(image_path, lang='hin+eng'):
    """Placeholder logic for Voter ID 6 (Hindi version)."""
    processed_img = preprocess_image(image_path)
    
    results = {
        'name_hindi': extract_text_from_roi(processed_img, 100, 100, 500, 50, lang=lang),
        'name_english': extract_text_from_roi(processed_img, 100, 200, 500, 50, lang='eng'),
    }
    
    return results
