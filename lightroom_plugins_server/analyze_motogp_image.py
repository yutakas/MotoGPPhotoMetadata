import os
import cv2
import numpy as np
from ultralytics import YOLO
import torch
import gc


home_path = os.environ['HOME']

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


def compute_laplacian_variance(cv2_image, yolo_results):
    laplacian_variance = 0.0
    tenengrad = 0.0
    rect = get_largest_motorcycle_rect(yolo_results)
    if rect is not None:
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

    torch.cuda.empty_cache()
    gc.collect()

    return laplacian_variance, tenengrad


def compute_keywords(cv2_image, yolo_results, laplacian_variance, tenengrad):
    keywords = {}


    shape = cv2_image.shape

    rect = get_largest_motorcycle_rect(yolo_results)
    if rect is not None:
        print('motorcycle_rect ' + str(rect))

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
        print('image_size ' + str(image_size))
        print('motorcycle_size ' + str(motorcycle_size))
        keywords['motorcyclesize'] = str(int(motorcycle_size / image_size * 10.0 + 1.0) * 10)

        keywords['laplacianvariance'] = str(int(laplacian_variance / 10.0 + 1.0) * 10)
        keywords['tenengrad'] = str(int(tenengrad / 10.0 + 1.0) * 10)

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

def analyze_image_from_bytes(image_bytes):
    nparr = np.frombuffer(image_bytes, np.uint8)
    cv2_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    # cv2.imwrite("output_image.jpg", cv2_image)

    yolo_results = run_YOLO_model(cv2_image)
    laplacian_variance, tenengrad = compute_laplacian_variance(cv2_image, yolo_results)
    keywords = compute_keywords(cv2_image, yolo_results, laplacian_variance, tenengrad)


    return keywords