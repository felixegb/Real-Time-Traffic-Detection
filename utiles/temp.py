import requests
import json

def fetch_weather_data():
    global api_key
    global base_url
    api_key = "c952a7664f352337df87d2f01c73725d"
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    params = {
    "lat": 36.529864,    
    "lon": -6.289932,  
    "appid": api_key,  
    "units": "metric"  
    }

    response = requests.get(base_url, params=params)
    data = json.loads(response.text)
    
    des = data['weather'][0]['description']
    temp = data['main']['temp']
    hum = data['main']['humidity']
    vel = data['wind']['speed']
    city = data['name']
    
    return des, temp, hum, vel, city

def fetch_weather_datao():
    params = {
    "lat": 35.693587,    
    "lon": 39.699156,  
    "appid": api_key,  
    "units": "metric"  
    }

    response = requests.get(base_url, params=params)   
    data = json.loads(response.text)
    
    des = data['weather'][0]['description']
    temp = data['main']['temp']
    hum = data['main']['humidity']
    vel = data['wind']['speed']
    city = data['name']
    
    return des, temp, hum, vel, city



