import os
import re
import numpy as np 
import pandas as pd 
import io
import math
import fitz
import pdfplumber
import pytesseract
import cv2





def bytes_to_cv2_image(img_bytes:bytes):
    arr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    return img

def img_has_text(img_bytes:bytes , word_threshold=5) -> int:
    img = bytes_to_cv2_image(img_bytes)
    try:
        text = pytesseract.image_to_string(img, lang='eng')
    except Exception:
        return 0
    words = re.findall(r'\w+' , text)
    return len(words)
def is_graphic_chart(img_bytes:bytes , line_threshold = 8 , rect_threshold = 3) -> bool:
    img = bytes_to_cv2_image(img_bytes)
    gray = cv2.cvtColor(img , cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3,3) , 0)
    edges = cv2.Canny(gray , 50 , 150)

    #Detect Line/Bar Charts
    lines = cv2.HoughLinesP(edges , 1 , np.pi/180 , 100 , 50 , 20)
    if lines is not None and len(lines)>= line_threshold:
        return True
    _ , thresh = cv2.threshold(gray , 0 , 255 , cv2.THRESH_BINARY + cv2.THRESH_OTSU )
    cnts , _ = cv2.findContours(thresh , cv2.RETR_EXTERNAL , cv2.CHAIN_APPROX_SIMPLE)

    #Rectangles
    rect_count = 0
    h_img , w_img = gray.shape
    for c in cnts:
        x, y, h, w = cv2.boundingRect(c)
        if w*h < 0.005* w_img * h_img:
            continue
        aspect_ratio = w / (h + 1e-6)
        if aspect_ratio < 0.5 or aspect_ratio > 2.0:
            rect_count += 1
    if rect_count >= rect_threshold:
        return True

def is_infographic(img_bytes: bytes , text_word_thresh = 8 ) -> bool:
    #img = bytes_to_cv2_image(img_bytes)
    word_count = img_has_text(img_bytes)
    if word_count >= text_word_thresh:
        return True
    if word_count >= (text_word_thresh//2) and is_graphic_chart(img_bytes):
        return True
    return False
def is_background_image(pix : fitz.Pixmap , page_pixmap_width , page_pixmap_height , ocr_text_thresh =3) -> bool:
    ih , iw = pix.height , pix.width
    w_ratio = iw/page_pixmap_width
    h_ratio = ih/page_pixmap_height
    if w_ratio > 0.88 and h_ratio > 0.88:
        b = pix.tobytes('png')
        words = img_has_text(b)
        if words <= ocr_text_thresh:
            return True
    return False








