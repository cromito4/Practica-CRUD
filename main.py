from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

# --------------------------------------------------
# PASO 1: La libreta donde guardamos las cosas (SQLite)
# --------------------------------------------------
# Esto crea automáticamente un archivo llamado "tiendita.db" en tu carpeta.
engine = create_engine("sqlite:///./tiendita.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# --------------------------------------------------
# PASO 2: El Modelo (Cómo se dibuja la tabla en la libreta)
# --------------------------------------------------
class TareaTabla(Base):
    __tablename__ = "tareas"

    id = Column(Integer, primary_key=True, index=True) # Un número único (1, 2, 3...)
    titulo = Column(String)                           # El nombre de la tarea
    completada = Column(Boolean, default=False)       # ¿Ya la hiciste? (True o False)

# Le decimos a SQLite: "Crea la tabla si no existe todavía"
Base.metadata.create_all(bind=engine)

# --------------------------------------------------
# PASO 3: El Esquema (El filtro de seguridad / Pydantic)
# --------------------------------------------------
# Esto es lo que el usuario TIENE que mandar para crear una tarea
class TareaEntrada(BaseModel):
    titulo: str

# --------------------------------------------------
# PASO 4: El Mesero (FastAPI con los 4 pedidos del CRUD)
# --------------------------------------------------
app = FastAPI(title="Mi Primer CRUD Sencillo")


# --- DOCUMENTACIÓN INTERACTIVA CON SCALAR ---
@app.get("/scalar", response_class=HTMLResponse, include_in_schema=False)
def ver_scalar():
    return """
    <!doctype html>
    <html>
      <head>
        <title>Mi Primer CRUD - Scalar API</title>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body>
        <script
          id="api-reference"
          data-url="/openapi.json">
        </script>
        <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
      </body>
    </html>
    """



# --- C: CREAR (POST) ---
@app.post("/tareas")
def crear_tarea(datos: TareaEntrada):
    db = SessionLocal() # 1. Abrimos la libreta
    
    nueva = TareaTabla(titulo=datos.titulo) # 2. Preparamos lo que vamos a escribir
    db.add(nueva)                           # 3. Lo anotamos
    db.commit()                             # 4. Guardamos los cambios
    db.refresh(nueva)                       # 5. Averiguamos qué ID le tocó
    
    db.close() # 6. Cerramos la libreta
    return {"mensaje": "¡Tarea creada con éxito!", "tarea": nueva}


# --- R: LEER / CONSULTAR (GET) ---
@app.get("/tareas")
def ver_todas_las_tareas():
    db = SessionLocal()
    todas = db.query(TareaTabla).all() # "Tráeme todo lo que haya anotado"
    db.close()
    return todas


# --- U: ACTUALIZAR (PUT) ---
# Por ejemplo, marcar la tarea con id=1 como completada
@app.put("/tareas/{tarea_id}")
def completar_tarea(tarea_id: int):
    db = SessionLocal()
    tarea = db.query(TareaTabla).filter(TareaTabla.id == tarea_id).first() # Buscarla
    
    if not tarea:
        db.close()
        raise HTTPException(status_code=404, detail="Esa tarea no existe")
    
    tarea.completada = True # Cambiamos su valor a hecha
    db.commit()             # Guardamos el cambio
    db.refresh(tarea)
    db.close()
    return {"mensaje": "¡Tarea completada!", "tarea": tarea}


# --- D: BORRAR (DELETE) ---
@app.delete("/tareas/{tarea_id}")
def borrar_tarea(tarea_id: int):
    db = SessionLocal()
    tarea = db.query(TareaTabla).filter(TareaTabla.id == tarea_id).first()
    
    if not tarea:
        db.close()
        raise HTTPException(status_code=404, detail="Esa tarea no existe")
    
    db.delete(tarea) # La borramos
    db.commit()      # Confirmamos el borrado
    db.close()
    return {"mensaje": f"La tarea {tarea_id} fue eliminada"}