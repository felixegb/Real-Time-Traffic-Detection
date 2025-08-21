from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
from tensorflow.keras.models import load_model
import uvicorn

# Cargar el modelo entrenado
model = load_model('app/lstm6.keras')

# Definir FastAPI
app = FastAPI()

# Definir la estructura de los datos de entrada
class InputData(BaseModel):
    manual_data: list

# Función para preparar la secuencia para la LSTM
def prepare_manual_sequence(manual_data, look_back, n_features):
    if len(manual_data) != look_back:
        raise ValueError(f"Se requieren {look_back} conjuntos de datos para una secuencia, pero se recibieron {len(manual_data)}.")
    sequence = np.array(manual_data).reshape(1, look_back, n_features)
    return sequence

@app.post("/predict/")
def predict(input_data: InputData):
    try:
        look_back = 6
        n_features = len(input_data.manual_data[0])
        
        # Preparar secuencia
        X_manual_seq = prepare_manual_sequence(input_data.manual_data, look_back, n_features)
        
        # Realizar predicción
        prediction = model.predict(X_manual_seq)
        
        
        # Retornar la respuesta como JSON
        return {
            "conteo_in": round(int(prediction[0][0]), 0),
            "conteo_out": round(int(prediction[0][1]), 0)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8001)