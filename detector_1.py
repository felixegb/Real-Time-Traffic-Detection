import cv2
import numpy as np
import math
from ultralytics import YOLO
from utiles.sort import *
import cvzone
import threading
import time


conteo_global_in = 0
conteo_global_out = 0
conteo_global_in_a = 0
conteo_global_out_a = 0
car_in = 0
bus_in = 0
truck_in = 0
car_out = 0
bus_out = 0
truck_out = 0
conteo_out = []
conteo_in = []
lock = threading.Lock()


# inicializa yolo, mascara y sort (rastreador)
def initialize_model_tracker_1(model_path, mask_path):
    model = YOLO(model_path)
    mask = cv2.imread(mask_path)
    tracker = Sort(max_age=20, min_hits=3, iou_threshold=0.3)
    return model, mask, tracker

# procesamiento de frames 
def process_frame(frame, mask, model, classNames, tracker, limites_out, conteo_out, limites_in, conteo_in):
    global conteo_global_in, conteo_global_out
    global car_out,  car_in,  bus_out,  bus_in,  truck_out,  truck_in
    
    # Usar atributos de función en lugar de variables globales
    if not hasattr(process_frame, 'vehicle_counts_in'):
        process_frame.vehicle_counts_in = {
            'car': 0,
            'bus': 0,
            'truck': 0
        }
    
    if not hasattr(process_frame, 'vehicle_counts_out'):
        process_frame.vehicle_counts_out = {
            'car': 0,
            'bus': 0,
            'truck': 0
        }
    
    if not hasattr(process_frame, 'vehicle_types'):
        process_frame.vehicle_types = {}
        
    if hasattr(process_frame, 'vehicle_counts_in') and hasattr(process_frame, 'vehicle_counts_out'):
       
        car_in = process_frame.vehicle_counts_in.get('car', 0)
        car_out = process_frame.vehicle_counts_out.get('car', 0)
        bus_in = process_frame.vehicle_counts_in.get('bus', 0)
        bus_out = process_frame.vehicle_counts_out.get('bus', 0)
        truck_in = process_frame.vehicle_counts_in.get('truck', 0)
        truck_out = process_frame.vehicle_counts_out.get('truck', 0)
    
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
            
            if clase_detect in ['bus', 'car', 'truck'] and conf > 0.5:
                currentArray = np.array([x1, y1, x2, y2, conf])
                detecciones = np.vstack((detecciones, currentArray))
                current_types[(x1,y1,x2,y2)] = clase_detect                # Guardar el tipo detectado para esta región
    
    result_tracker = tracker.update(detecciones)
    
    # Dibujar líneas de conteo
    cv2.line(frame, (limites_out[0], limites_out[1]), (limites_out[2], limites_out[3]), (0, 0, 255), 5)
    cv2.line(frame, (limites_in[0], limites_in[1]), (limites_in[2], limites_in[3]), (0, 0, 255), 5)
    
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
        
        # Si no se encuentra tipo, usar el último conocido
        if vehicle_type is None:
            vehicle_type = process_frame.vehicle_types.get(id, 'unknown')
        else:
            process_frame.vehicle_types[id] = vehicle_type
        
        # Dibujar bbox y etiqueta
        cvzone.cornerRect(frame, (x1, y1, w, h), l=3, rt=1, colorR=(255, 0, 255))
        cvzone.putTextRect(frame, f'{vehicle_type}', (max(0, x1), max(35, y1)), 
                          scale=0.6, thickness=1, offset=1)
        
        cx, cy = x1 + w // 2, y1 + h // 2
        cv2.circle(frame, (cx, cy), 5, (0, 255, 0), cv2.FILLED)
        
        # Conteo
        #with lock:
        if limites_out[0] < cx < limites_out[2]  + 10 and limites_out[1] - 20 < cy < limites_out[1] + 10:
            if conteo_out.count(id) == 0:
                conteo_out.append(id)
                if vehicle_type in process_frame.vehicle_counts_out:
                    process_frame.vehicle_counts_out[vehicle_type] += 1
        
        if limites_in[0] + 5 < cx < limites_in[2] and limites_in[1] - 20 < cy < limites_in[1] + 20:
            if conteo_in.count(id) == 0:
                conteo_in.append(id)
                if vehicle_type in process_frame.vehicle_counts_in:
                    process_frame.vehicle_counts_in[vehicle_type] += 1
                              
    conteo_global_in = len(conteo_in)
    conteo_global_out = len(conteo_out)
    # Mostrar conteos
    '''y_pos = 50
    for vehicle_type in ['car', 'bus', 'truck']:
        cvzone.putTextRect(frame, f'{vehicle_type.capitalize()} IN: {process_frame.vehicle_counts_in[vehicle_type]}',
                          (50, y_pos), colorR=(255, 0, 0), scale=1.2, thickness=2)
        y_pos += 40
    
    y_pos = 50
    for vehicle_type in ['car', 'bus', 'truck']:
        cvzone.putTextRect(frame, f'{vehicle_type.capitalize()} OUT: {process_frame.vehicle_counts_out[vehicle_type]}',
                          (300, y_pos), colorR=(0, 0, 255), scale=1.2, thickness=2)
        y_pos += 40'''
    
    return frame, region, conteo_in, conteo_out
    
    #return frame, conteo_in, region, conteo_out


def get_conteo_global(): 
    return conteo_global_in, conteo_global_out
def get_conteo_global_a(): 
    return conteo_global_in_a, conteo_global_out_a

 
def individual ():  
    return car_in,car_out,bus_in, bus_out,truck_in,truck_out

#conteo_out = [] 
#conteo_in = []

def reset_counter_thread(): #reiniciando variables
    global conteo_global_in_a, conteo_global_out_a
    while True:
        time.sleep(300) 
        with lock:
            conteo_global_in_a = len(conteo_in)
            conteo_global_out_a = len(conteo_out)  
            conteo_out.clear()
            conteo_in.clear()
            
            if hasattr(process_frame, 'vehicle_counts_in'):
                process_frame.vehicle_counts_in = {
                    'car': 0,
                    'bus': 0,
                    'truck': 0
                }
            if hasattr(process_frame, 'vehicle_counts_out'):
                process_frame.vehicle_counts_out = {
                    'car': 0,
                    'bus': 0,
                    'truck': 0
                }

reset_thread = threading.Thread(target=reset_counter_thread, daemon=True)
reset_thread.start()  


def process_video_streamc(stream_url, model, mask, tracker, classNames, limites_out, limites_in):
    global conteo_in,conteo_out
    captura_video = cv2.VideoCapture(stream_url)
    conteo_out = [] 
    conteo_in = []
    frame_count = 0
    fps = 20
    frame_skip = int(captura_video.get(cv2.CAP_PROP_FPS) // fps)

    while captura_video.isOpened():
        success, frame = captura_video.read()
        if not success:
            break
        if frame_count % frame_skip != 0:
            frame_count += 1
            continue

        frame, region, conteo_in, conteo_out = process_frame(frame, mask, model, classNames, 
                                                             tracker, limites_out, conteo_out, 
                                                             limites_in, conteo_in)
        yield frame
        frame_count += 1

    captura_video.release()
    cv2.destroyAllWindows()




