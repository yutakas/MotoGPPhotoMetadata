import os
import json
import logging
import cv2
import numpy as np
from ultralytics import YOLO
import torch
import gc
import analyze_with_openai_api

logger = logging.getLogger('motogp_server.analyze')


home_path = os.environ['HOME']

_CACHE_FILE = os.path.join(os.path.dirname(__file__), 'openai_cache.json')

def _load_cache():
    if os.path.exists(_CACHE_FILE):
        with open(_CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def _save_cache(cache):
    with open(_CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)

_openai_cache = _load_cache()

def get_largest_motorcycle_rect(yolo_results):
    motorcycle_rects = []
    for result in yolo_results:
        xyxys = result['xyxy'].tolist()
        clses = result['cls'].tolist()
        for c, r in zip(clses, xyxys):
            if c == 3.0:
                motorcycle_rects.append(r)
    if not motorcycle_rects:
        return None
    return max(motorcycle_rects, key=lambda r: abs(r[2] - r[0]) * abs(r[3] - r[1]))


def compute_laplacian_variance(cv2_image, rect):
    laplacian_variance = 0.0
    tenengrad = 0.0
    x1, y1, x2, y2 = map(int, rect)
    x1_center = int((x1 + x2) / 2 - (x2 - x1) / 4)
    x2_center = int((x1 + x2) / 2 + (x2 - x1) / 4)
    y1_center = int((y1 + y2) / 2 - (y2 - y1) / 4)
    y2_center = int((y1 + y2) / 2 + (y2 - y1) / 4)
    cropped_img = cv2_image[y1_center:y2_center, x1_center:x2_center]
    try:
        gray = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        laplacian_variance = laplacian.var()
        gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        tenengrad = (gx**2 + gy**2).mean()
    except Exception:
        pass
    return laplacian_variance, tenengrad

def analyze_with_llm(motorcycle_img, openai_api_key='', openai_model='', image_path='', image_bytes=None):
    return analyze_with_openai_api.get_openai_analysis(motorcycle_img, openai_api_key=openai_api_key, openai_model=openai_model, image_path=image_path, image_bytes=image_bytes)

def compute_keywords(cv2_image, yolo_results, image_path='', openai_api_key='', openai_model='', image_bytes=None, force_update=False):
    keywords = {}

    shape = cv2_image.shape

    rect = get_largest_motorcycle_rect(yolo_results)
    if rect is not None:
        logger.info('motorcycle_rect %s', rect)
        x1, y1, x2, y2 = map(int, rect)
        motorcycle_img = cv2_image[y1:y2, x1:x2]
        cv2.imwrite("output_image.jpg", motorcycle_img)

        frame_in_edge = 0.02
        if (rect[0] > float(shape[1]) * frame_in_edge) & \
        (shape[1] - rect[2] > float(shape[1]) * frame_in_edge) & \
        (rect[1] > float(shape[0]) * frame_in_edge) & \
        (shape[0] - rect[3] > float(shape[0]) * frame_in_edge):
            keywords['inframed'] = "true"
        else:
            keywords['inframed'] = "false"

        center_edge = 0.10
        motorcycle_center_x = (rect[2] - rect[0] / 2.0) + rect[0]
        motorcycle_center_y = (rect[3] - rect[1] / 2.0) + rect[1]
        if (motorcycle_center_x > float(shape[1]) - float(shape[1]) * center_edge) & \
        (motorcycle_center_x < float(shape[1]) + float(shape[1]) * center_edge) & \
        (motorcycle_center_y > float(shape[0]) - float(shape[0]) * center_edge) & \
        (motorcycle_center_y < float(shape[0]) + float(shape[0]) * center_edge):
            keywords['centered'] = "true"
        else:
            keywords['centered'] = "false"

        image_size = float(shape[1]) * float(shape[0])
        motorcycle_size = abs(rect[2] - rect[0]) * abs(rect[3] - rect[1])
        logger.info('image_size %s', image_size)
        logger.info('motorcycle_size %s', motorcycle_size)
        keywords['motorcyclesize'] = str(int(motorcycle_size / image_size * 10.0 + 1.0) * 10)

        laplacian_variance, tenengrad = compute_laplacian_variance(cv2_image, rect)
        keywords['laplacianvariance'] = str(int(laplacian_variance / 10.0 + 1.0) * 10)
        keywords['tenengrad'] = str(int(tenengrad / 10.0 + 1.0) * 10)

        if not force_update and image_path and image_path in _openai_cache:
            openai_analysis = _openai_cache[image_path]
        else:
            openai_analysis = analyze_with_llm(motorcycle_img, openai_api_key=openai_api_key, openai_model=openai_model, image_path=image_path, image_bytes=image_bytes)
            if image_path and openai_analysis is not None:
                _openai_cache[image_path] = openai_analysis
                _save_cache(_openai_cache)
        if openai_analysis is not None:
            keywords['motogp_team'] = openai_analysis.get('motogp_team', '')
            keywords['bike_color'] = openai_analysis.get('bike_color', '')
            # keywords['sponsor_names'] = openai_analysis.get('sponsor_names', '')
            # keywords['logos'] = openai_analysis.get('logos', '')

    torch.cuda.empty_cache()
    gc.collect()

    return keywords


def run_YOLO_model(cv2_image):
    model = YOLO( os.path.join(home_path, 'src/github/MotoGPPhotoMetadata/models/yolo12x.pt'))

    results = model(source=cv2_image, show=False, conf=0.8, save=False, device='mps')
    # results = model(source=file_path, show=False, conf=0.8, save=False, device='mps')
    yolo_results = []
    for res in results:
        boxes = None
        clses = None
        try:
            if hasattr(res, "boxes"):
                boxes = res.boxes.xyxy.cpu().numpy()      # shape (N,4)
                clses = res.boxes.cls.cpu().numpy()      # shape (N,)
        except Exception:
            # fallback: try to access as list / numpy already
            try:
                boxes = getattr(res.boxes, "xyxy", None)
                clses = getattr(res.boxes, "cls", None)
            except Exception:
                boxes = None
                clses = None        
        yolo_results.append({"xyxy": boxes, "cls": clses})
    del res
    torch.cuda.empty_cache()
    gc.collect()

    return yolo_results

def analyze_image_from_bytes(image_bytes, image_path='', openai_api_key='', openai_model='', force_update=False):
    nparr = np.frombuffer(image_bytes, np.uint8)
    cv2_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    # cv2.imwrite("output_image.jpg", cv2_image)

    logger.info("Analyzing image: %s (force_update=%s)", image_path, force_update)
    yolo_results = run_YOLO_model(cv2_image)

    keywords = compute_keywords(cv2_image, yolo_results, image_path, openai_api_key=openai_api_key, openai_model=openai_model, image_bytes=image_bytes, force_update=force_update)

    return keywords