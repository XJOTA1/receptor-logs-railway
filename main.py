from fastapi import FastAPI, Request
from sqlalchemy import create_engine, Column, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
import uvicorn

# Configuración de la Base de Datos (SQLite)
# Render/Railway generalmente crean esta base de datos si no existe.
SQLALCHEMY_DATABASE_URL = "sqlite:///./logs.db"

# engine: Objeto que gestiona la conexión a la base de datos.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} # Necesario solo para SQLite
)

# Base: Clase base para nuestros modelos
Base = declarative_base()

# Sesión: Objeto que usaremos para interactuar con la DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Definición del Modelo de Datos (La tabla 'logs')
class LogEntry(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow) # Hora de recepción
    raw_log = Column(Text) # Aquí se guarda el JSON completo como texto

# Crea las tablas en la base de datos si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Función para obtener la sesión de la DB (patrón de dependencia de FastAPI)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Ruta principal para recibir el Webhook
@app.post("/webhook")
async def recibir_logs(request: Request):
    db = next(get_db()) # Abrir la sesión de la DB

    try:
        log_data = await request.json()
    except Exception as e:
        print(f"Error al parsear el JSON: {e}")
        return {"status": "Error", "message": "JSON inválido"}, 400

    # ----------------------------------------------------
    # 1. GUARDAR EL LOG COMPLETO EN LA BASE DE DATOS
    # ----------------------------------------------------
    
    # Convertir el diccionario log_data a una cadena JSON para guardarlo en la columna Text
    raw_json_string = json.dumps(log_data)
    
    db_log = LogEntry(raw_log=raw_json_string)
    
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    
    # 2. LOGGING EN CONSOLA (Opcional, pero útil para verificar)
    print("="*50)
    print(f"✅ Log recibido y guardado en DB con ID: {db_log.id}")
    print(f"Estado de pago: {log_data.get('pagado', 'N/A')}")
    print("="*50)

    # 3. Respuesta final al emisor del webhook
    return {"status": "Guardado en DB", "id_guardado": db_log.id}

@app.get("/")
def home():
    return {"mensaje": "Receptor de Webhooks operativo. DB SQLite activa."}