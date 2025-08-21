from sqlalchemy import create_engine, Column, Integer, DateTime, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from detector_1 import get_conteo_global_a
from detector_2 import get_conteo_global_almacen
from utiles.temp import fetch_weather_data, fetch_weather_datao
from sqlalchemy import Float, String

DATABASE_URI = 'mysql+pymysql://root:root@localhost/mydatabase'
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)

Base = declarative_base()

class DatosCadiz(Base):
    __tablename__ = 'datos_cadiz'
    id = Column(Integer, primary_key=True, autoincrement=True)
    dia = Column(String(100))
    hora = Column(String(100))
    clima = Column(String(100))
    temperatura = Column(Float)
    humedad = Column(Float)
    viento = Column(Float)
    city = Column(String(100))
    conteo_in = Column(Integer)
    conteo_out = Column(Integer)
    
class DatosVigo(Base):
    __tablename__ = 'datos_vigo'
    id = Column(Integer, primary_key=True, autoincrement=True)
    dia = Column(String(100))
    hora = Column(String(100))
    clima = Column(String(100))
    temperatura = Column(Float)
    humedad = Column(Float)
    viento = Column(Float)
    city = Column(String(100))
    conteo_n = Column(Integer)
    conteo_s = Column(Integer)
    conteo_e = Column(Integer)
    conteo_o = Column(Integer)

Base.metadata.create_all(engine)


def hora_dia():
    ahora = datetime.now()
    dia_semana = ahora.weekday()
    tiempo = ahora.strftime("%H:%M")
    # Para mostrar el día como texto
    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    dia_actual = dias[dia_semana]
    return dia_actual, tiempo




def almacenar_conteo_1():
    conteo_in, conteo_out = get_conteo_global_a()
    clima, temperatura, humedad, viento, city = fetch_weather_data()
    dia_actual, tiempo = hora_dia()

    with Session() as session:
        nuevo_conteo = DatosCadiz(dia=dia_actual, hora = tiempo, clima=clima, 
                                  temperatura=temperatura, humedad=humedad, 
                                  viento=viento, city=city, conteo_in=conteo_in, 
                                  conteo_out=conteo_out)
        session.add(nuevo_conteo)
        session.commit()
        
def almacenar_conteo_2():
    conteo_global_n,conteo_global_s,conteo_global_e,conteo_global_o = get_conteo_global_almacen()
    clima, temperatura, humedad, viento, city = fetch_weather_datao()
    dia_actual, tiempo = hora_dia()
    

    with Session() as session:
        nuevo_conteo = DatosVigo(dia=dia_actual, hora = tiempo, clima=clima, temperatura=temperatura, humedad=humedad, viento=viento, city=city, conteo_n=conteo_global_n, conteo_s=conteo_global_s,conteo_e=conteo_global_e,conteo_o=conteo_global_o)
        session.add(nuevo_conteo)
        session.commit()
        
#if __name__ == '__main__':
    #almacenar_conteo_1()
    # almacenar_conteoo()
