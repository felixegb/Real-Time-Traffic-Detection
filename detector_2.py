import cv2
import numpy as np
import math
from ultralytics import YOLO
from utiles.sort import *
import cvzone
import random
import threading
import time


conteo_global_n,conteo_global_s,conteo_global_e,conteo_global_o = 0,0,0,0
conteo_global_na,conteo_global_sa,conteo_global_ea,conteo_global_oa = 0,0,0,0
conteo_n, conteo_s,conteo_e,conteo_o = [],[],[],[]

def initialize_model_tracker(model_path, mask_path):
    model = YOLO(model_path)
    mask = cv2.imread(mask_path)
    tracker = Sort(max_age=20, min_hits=3, iou_threshold=0.3)
    return model, mask, tracker


def process_frame(frame, mask, model, classNames, tracker, conteo_n,conteo_s,conteo_e,conteo_o,limites_n, limites_s,limites_e,limites_o ):
    global conteo_global_n, conteo_global_e, conteo_global_o, conteo_global_s
       
    frame = cv2.resize(frame, (832, 640))
    region = cv2.bitwise_and(frame, mask)
    
    # Procesar el frame una sola vez
    result = model(region, stream=True)
    detecciones = np.empty((0, 5))
    current_types = {}  # Almacenar tipos detectados en este frame
    
    for r in result:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = math.ceil(box.conf[0] * 100) / 100
            cls = int(box.cls[0])
            clase_detect = classNames[cls]
            
            if clase_detect in ['bus', 'car', 'truck'] and conf > 0.4:
                currentArray = np.array([x1, y1, x2, y2, conf])
                detecciones = np.vstack((detecciones, currentArray))
                # Guardar el tipo detectado para esta región
                current_types[(x1,y1,x2,y2)] = clase_detect
    
    result_tracker = tracker.update(detecciones) #seguimiento con sort
    
    # Dibujar líneas de conteo
    cv2.line(frame, (limites_n[0], limites_n[1]), (limites_n[2], limites_n[3]), (0, 0, 255), 5)
    cv2.line(frame, (limites_s[0], limites_s[1]), (limites_s[2], limites_s[3]), (0, 0, 255), 5)
    cv2.line(frame, (limites_e[0], limites_e[1]), (limites_e[2], limites_e[3]), (0, 0, 255), 5)
    cv2.line(frame, (limites_o[0], limites_o[1]), (limites_o[2], limites_o[3]), (0, 0, 255), 5)
    
    for result in result_tracker:
        x1, y1, x2, y2, id = map(int, result)
        w, h = x2 - x1, y2 - y1
        
        # Buscar el tipo de vehículo más cercano en las detecciones actuales
        vehicle_type = None
        min_distance = float('inf')
        for (dx1,dy1,dx2,dy2), tipo in current_types.items():
            distance = abs(x1-dx1) + abs(y1-dy1)
            if distance < min_distance:
                min_distance = distance
                vehicle_type = tipo
        
        # Dibujar bbox y etiqueta
        cvzone.cornerRect(frame, (x1, y1, w, h), l=3, rt=1, colorR=(255, 0, 255))
        cvzone.putTextRect(frame, f'{vehicle_type}', (max(0, x1), max(35, y1)), 
                          scale=0.6, thickness=1, offset=1)
        
        cx, cy = x1 + w // 2, y1 + h // 2
        cv2.circle(frame, (cx, cy), 5, (0, 255, 0), cv2.FILLED)
        
        # Conteo
        if limites_n[0] < cx < limites_n[2] and limites_n[1] - 10 < cy < limites_n[1] + 20:
            if conteo_n.count(id) == 0:
                conteo_n.append(id)
                '''if vehicle_type in process_frame.vehicle_counts_out:
                    process_frame.vehicle_counts_out[vehicle_type] += 1'''
        
        if limites_s[0] < cx < limites_s[2] and limites_s[1] - 10 < cy < limites_s[1] + 120:
            if conteo_s.count(id) == 0:
                conteo_s.append(id)
                '''if vehicle_type in process_frame.vehicle_counts_in:
                    process_frame.vehicle_counts_in[vehicle_type] += 1'''
        
        if limites_e[0] < cx < limites_e[2] and limites_e[1] - 120 < cy < limites_e[1]:
            if conteo_e.count(id) == 0:
                conteo_e.append(id)
                '''if vehicle_type in process_frame.vehicle_counts_out:
                    process_frame.vehicle_counts_out[vehicle_type] += 1'''
        
        if limites_o[0] < cy < limites_o[2] and limites_o[1] - 80 < cx < limites_o[1]:
            if conteo_o.count(id) == 0:
                conteo_o.append(id)
                '''if vehicle_type in process_frame.vehicle_counts_in:
                    process_frame.vehicle_counts_in[vehicle_type] += 1'''
                    
    conteo_global_n = len(conteo_n)
    conteo_global_s = len(conteo_s)
    conteo_global_e = len(conteo_e)
    conteo_global_o = len(conteo_o)
        
    return frame, region, conteo_n, conteo_s, conteo_e, conteo_o



def get_conteo_globalo(): 
    return conteo_global_n,conteo_global_s,conteo_global_e,conteo_global_o
def get_conteo_global_almacen(): 
    return conteo_global_na,conteo_global_sa,conteo_global_ea,conteo_global_oa

    
def reset_counter_thread(): #reiniciando variables
    global conteo_global_na,conteo_global_sa,conteo_global_ea,conteo_global_oa
    while True:
        time.sleep(300)
        conteo_global_na = len(conteo_n)                          
        conteo_global_sa = len(conteo_s)
        conteo_global_ea = len(conteo_e)                          
        conteo_global_oa = len(conteo_o)
        conteo_n.clear()
        conteo_s.clear()
        conteo_e.clear()
        conteo_o.clear()
            
# Iniciar el thread de reinicio antes del loop principal
reset_thread = threading.Thread(target=reset_counter_thread, daemon=True)
reset_thread.start()

# Procesa el stream de video
def process_video_stream(stream_url, model, mask, tracker, classNames,limites_n, limites_s,limites_e,limites_o):
    global conteo_n, conteo_s, conteo_e, conteo_o
    cap = cv2.VideoCapture(stream_url)
    conteo_n = [] 
    conteo_s = []
    conteo_e = []
    conteo_o = []
    frame_count = 0
    fps = 20
    frame_skip = int(cap.get(cv2.CAP_PROP_FPS) // fps)

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        if frame_count % frame_skip != 0:
            frame_count += 1
            continue

        frame, region, conteo_n,conteo_s,conteo_e,conteo_o = process_frame(frame, mask, model, classNames, tracker, conteo_n,conteo_s,conteo_e,conteo_o,limites_n, limites_s,limites_e,limites_o )
        yield frame
        frame_count += 1

    cap.release()
    cv2.destroyAllWindows()

