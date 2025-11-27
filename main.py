from fastapi import FastAPI, Request
import uvicorn
import json

app = FastAPI()

# Esta es la ruta donde tu Webhook enviará los datos
@app.post("/webhook")
async def recibir_logs(request: Request):
    
    # Intentamos leer los datos entrantes. Es crucial manejar errores.
    try:
        # Usamos request.json() para leer el cuerpo de la petición como un diccionario Python
        log_data = await request.json()
    except Exception as e:
        # Si el cuerpo no es JSON válido, devolvemos un error 400
        print(f"Error al parsear el JSON: {e}")
        return {"status": "Error", "message": "JSON inválido"}, 400

    # =======================================================
    # LÓGICA DE REGISTRO DE DATOS CRUDOS
    # =======================================================
    
    print("\n" + "="*50)
    print("📢 LOG COMPLETO RECIBIDO:")
    
    # Imprimimos el JSON completo formateado para que sea legible en los logs de Railway
    # El ID se usa para rastrear el evento
    id_principal = log_data.get('id', 'N/A')
    print(f"ID de Evento: {id_principal}")
    
    # Imprimimos el log completo. Usa esta línea para ver la estructura.
    print(json.dumps(log_data, indent=4))
    
    print("="*50 + "\n")

    # Devolvemos 200 OK para confirmar la recepción exitosa.
    return {"status": "Recibido OK", "mensaje": "Log capturado para su posterior análisis"}

@app.get("/")
def home():
    # Ruta simple para verificar que el servidor está encendido
    return {"mensaje": "Receptor de Webhooks operativo. Esperando POST en /webhook"}