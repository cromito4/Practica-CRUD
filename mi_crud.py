from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

# paso 1
engine = create_engine("sqlite:///./mi_base_de_datos.db", connect_args={"check_same_thread": False})

session_local = sessionmaker(bind=engine)

base = declarative_base()

# paso 2
class tarea(base):
    __tablename__ = "tareas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String)
    desarrollado_por = Column(String)
    completada = Column(Boolean, default=False)

base.metadata.create_all(bind=engine)

# paso 3
class TareaEntrada(BaseModel):
    titulo: str
    desarrollado_por: str

# paso 4
app = FastAPI(title="El crud hecho con mis propieas manos. let's gooo!")

# --- DOCUMENTACIÓN INTERACTIVA EN SCALAR ---
@app.get("/scalar", response_class=HTMLResponse, include_in_schema=False)
def ver_scalar():
    return """
    <!doctype html>
    <html>
      <head>
        <title>El CRUD hecho con mis propias manos - Scalar</title>
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

@app.post("/tareas")
def crear_tarea(datos: TareaEntrada):
    db = session_local()
    nueva = tarea(titulo=datos.titulo, desarrollado_por = datos.desarrollado_por)
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    db.close()
    return nueva

# paso 5
@app.get("/tareas")
def ver_tareas():
    db = session_local()
    todas = db.query(tarea).all()
    db.close()
    return todas

# paso 6
@app.put("/tareas/{tarea_id}")
def completar_tarea(tarea_id: int):
    db = session_local()
    tarea_encontrada = db.query(tarea).filter(tarea.id == tarea_id).first()

    if not tarea_encontrada:
        db.close()
        raise HTTPException(status_code=404, detail="Esa tarea no existe")

    tarea_encontrada.completada = True
    db.commit()
    db.refresh(tarea_encontrada)
    db.close()
    return tarea_encontrada

# paso 7
@app.delete("/tareas/{tarea_id}")
def borrar_tarea(tarea_id: int):
    db = session_local()
    tarea_encontrada = db.query(tarea).filter(tarea.id == tarea_id).first()

    if not tarea_encontrada:
        db.close()
        raise HTTPException(status_code=404, detail="Esa tarea no existe")

    db.delete(tarea_encontrada)
    db.commit()
    db.close()
    return tarea_encontrada