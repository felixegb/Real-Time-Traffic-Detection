import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sqlalchemy import create_engine

# Conectar a la base de datos MySQL
engine = create_engine('mysql+pymysql://root:root@localhost/mydatabase')

# Inicializar el scaler
scaler = MinMaxScaler()

# Función para convertir horas a minutos
def time_to_minutes(time_str):
    hours, minutes = map(int, time_str.split(':'))
    return hours * 60 + minutes

# Función para procesar los datos antes de la predicción
def process_data():
    # Consulta SQL para obtener los últimos 6 registros
    query = '''
    SELECT dia, hora FROM (
        SELECT * FROM datos_cadiz ORDER BY id DESC LIMIT 6
    ) subquery ORDER BY id ASC;
    '''
    df = pd.read_sql(query, con=engine)
    print(df)

    # Formatear la hora correctamente
    #df["hora"] = df["hora"].dt.components.hours.astype(str) + ":" + df["hora"].dt.components.minutes.astype(str).str.zfill(2)
    df["hora"] = pd.to_datetime(df["hora"], format="%H:%M", errors="coerce").dt.strftime("%H:%M")
    df['hora'] = df['hora'].apply(time_to_minutes)

    # Mapear los días a números
    days_mapping = {'Lunes': 1, 'Martes': 2, 'Miércoles': 3, 'Jueves': 4, 'Viernes': 5, 'Sabado': 6, 'Domingo': 7}
    df['dia'] = df['dia'].map(days_mapping)

    # Normalizar la hora usando el scaler ya ajustado
    df[['hora']] = scaler.transform(df[['hora']])
    df['hora'] = df['hora'].round(7)
    
    # Convertir a JSON
    return {"manual_data": df.values.tolist()}

# Cargar dataset de referencia y ajustar el scaler
df_s = pd.read_csv('./static/data_scaler.csv')
df_s['hora'] = df_s['hora'].str.strip().apply(time_to_minutes)
df_s[['hora']] = scaler.fit_transform(df_s[['hora']])