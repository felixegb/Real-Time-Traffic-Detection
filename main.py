import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocketDisconnect, WebSocket,HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from fastapi.templating import Jinja2Templates
import uvicorn
import requests
import httpx
from detector_1 import *
from detector_2 import *
from utiles.almacenamiento import *
from fastapi.middleware.cors import CORSMiddleware
from utiles.utils import get_stream_url_1, get_stream_url_2
from utiles.temp import fetch_weather_data, fetch_weather_datao
from utiles.data_pro import process_data



@asynccontextmanager
async def lifespan(app: FastAPI):
    almacenar_task = asyncio.create_task(almacenar_data())
    try:
        yield
    finally:
        almacenar_task.cancel()
        try:
            await almacenar_task
        except asyncio.CancelledError:
            print("Cancelada ")



app = FastAPI (lifespan=lifespan) 

prediction_task = None
is_running = False
running= ''
predict_in = 0
predict_out = 0

origen = [ "http://localhost:8000" ]
          
app.add_middleware(
    CORSMiddleware,
    allow_origins=origen, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

 
templates = Jinja2Templates(directory="./static")
PREDICTION_URL = "http://127.0.0.1:8001/predict/"

#  estaticos
app.mount("/static", StaticFiles(directory="static/"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

    
async def almacenar_data():
    while True:
        await asyncio.sleep(310)
        almacenar_conteo_1()
        almacenar_conteo_2()
       

async def fetch_prediction():
    global is_running, predict_in, predict_out, running
    is_running = True
    async with httpx.AsyncClient() as client:
        while is_running:
            try:
                data = await asyncio.to_thread(process_data)
                response = await client.post(PREDICTION_URL, json=data)
                response.raise_for_status()
                result = response.json()
                predict_in = result.get('conteo_in')
                predict_out = result.get('conteo_out')
                print(predict_in, predict_out) 
                await asyncio.sleep(240)

            except Exception as e:
                is_running = False
    is_running = False
    
    

@app.post("/start_prediction")
async def start_prediction():
    global prediction_task, is_running, running
    prediction_task = asyncio.create_task(fetch_prediction())
    running = 'Activada'
    

@app.post("/stop_prediction")
async def stop_prediction():
    global prediction_task, is_running, running, predict_in, predict_out
    is_running = False
    running = 'Desactivada'
    predict_in = 0
    predict_out = 0
    prediction_task.cancel() 
    prediction_task = None
    
    
@app.get("/prediction-status")
async def get_prediction_status():
    
    return {
        "running": is_running,
        "predict_in": predict_in,
        "predict_out": predict_out,
    }
                        

@app.get("/video_feed_cadiz")
async def video_feed_cadiz():
    def generate_frames():
        stream_url = get_stream_url_1("https://youtu.be/0dKNLFFcHFU") 
        model, mask, tracker = initialize_model_tracker_1('modelos/modelo.pt', 'static/todascopia.png')
        classNames = ["bus", "car", "truck"]
        limites_out = [10, 437, 140, 437]
        limites_in = [ 165, 437, 850,437]
        for frame in process_video_streamc(stream_url, model, mask, tracker, classNames, limites_out, limites_in):
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    return StreamingResponse(generate_frames(), media_type='multipart/x-mixed-replace; boundary=frame')



@app.get("/video_feed_otra")
async def video_feed_otra():
    def generate_frames():
        stream_url = get_stream_url_2('https://youtu.be/6dp-bvQ7RWo')     #("https://youtu.be/6dp-bvQ7RWo")
        model, mask, tracker = initialize_model_tracker('modelos/828j.pt', 'static/todascopia.png')
        classNames = ["bus", "car", "truck"]
        limites_n = [370, 110, 400, 115]
        limites_s = [60, 400, 100, 520]
        limites_e = [470, 240, 530, 170]
        limites_o = [90, 250, 200, 180]
        

        for frame in process_video_stream(stream_url, model, mask, tracker, classNames, limites_n, limites_s,limites_e,limites_o):
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    return StreamingResponse(generate_frames(), media_type='multipart/x-mixed-replace; boundary=frame')



@app.websocket("/ws/conteo_1")
async def websocket_endpoint_conteo_1(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            conteo_global_in, conteo_global_out = get_conteo_global()
            conteo_g_in, conteo_g_out = get_conteo_global_a()
            car_in,car_out,bus_in, bus_out,truck_in,truck_out = individual()
            message = (f"{conteo_global_in},{conteo_global_out},{predict_in},"
                       f"{predict_out},{car_in},{car_out},{bus_in},{bus_out},"
                       f"{truck_in},{truck_out},{conteo_g_in}, {conteo_g_out}, {running}")
            await websocket.send_text(message)
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        print("WebSocket desconectado")
        
@app.websocket("/ws/conteo_2")
async def websocket_endpoint_conteo_2(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            conteo_global_n,conteo_global_s,conteo_global_e,conteo_global_o = get_conteo_globalo()
            conteo_global_na,conteo_global_sa,conteo_global_ea,conteo_global_oa = get_conteo_global_almacen()
            message_2= (f"{conteo_global_n},{conteo_global_s},{conteo_global_e},{conteo_global_o},"
                        f"{conteo_global_na},{conteo_global_sa},{conteo_global_ea},{conteo_global_oa}")
           
            await websocket.send_text(message_2)
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        print("WebSocket desconectado")

@app.websocket("/ws/clima")
async def websocket_endpoint_clima(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            des, temp, hum, vel, city = fetch_weather_data()
            des1, temp2, hum3, vel4, city5 = fetch_weather_datao()
            await websocket.send_text(f'{des},{temp},{hum},{vel},{city},{des1},{temp2},{hum3},{vel4},{city5}')
            await asyncio.sleep(600)
    except (WebSocketDisconnect, asyncio.CancelledError):
        print("WebSocket cerrado")
        

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)  






