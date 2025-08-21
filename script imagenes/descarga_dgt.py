import os
import requests
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from bs4 import BeautifulSoup
import time 
import datetime as datetime

def ejecutar_descarga():
    os.makedirs("imagenes_dgt", exist_ok=True)

    # Configurar Microsoft Edge
    options = Options()
    options.use_chromium = True
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")

    driver = webdriver.Edge(
        service=Service(EdgeChromiumDriverManager().install()),
        options=options
    )

    try:
        url = "https://www.dgt.es/conoce-el-estado-del-trafico/camaras-de-trafico/?pag=119&prov=&carr="
        driver.get(url)
        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        imagenes = soup.find_all("img", attrs={"data-img": True})
        urls = [img["data-img"] for img in imagenes]
        fecha_hora_actual = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Descarga
        for i, img_url in enumerate(urls):
            try:
                response = requests.get(img_url)
                if response.status_code == 200:
                    nombre_archivo = f"imagenes_dgt/imagen{i+1}_{fecha_hora_actual}.jpg"
                    with open(nombre_archivo, "wb") as f:
                        f.write(response.content)
                    print(f"Imagen {i+1} descargada")
                else:
                    print(f"Error al descargar imagen {i+1}: {response.status_code}")
            except Exception as e:
                print(f"Error al descargar desde {img_url}: {e}")
    finally:
        driver.quit()
 
while True:
    print("Descargando")
    try:
        ejecutar_descarga()
    except Exception as e:
        print(f"Error: {e}")

    print("10 minutos\n")
    time.sleep(600) 