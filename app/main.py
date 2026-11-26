from fastapi import FastAPI, HTTPException 
from pydantic import BaseModel 
from app.database import get_connection, create_table

app = FastAPI()
create_table()  # Crear la tabla al iniciar la aplicación 

class Tarea(BaseModel):
    titulo: str
    descripcion: str | None = None
    completada: bool = False 

@app.get("/")
def inicio():
    return {"mensaje": "FUNCIONAAAAAA!!!!!!!!"}


@app.post("/tareas")
def crear_tarea(tarea: Tarea):
    conn = get_connection()
    cursor = conn.execute("INSERT INTO tareas (titulo, descripcion, completada) VALUES (?, ?, ?)",(tarea.titulo, tarea.descripcion, int(tarea.completada)))
    conn.commit()
    nuevo_id = cursor.lastrowid 
    conn.close()
    return {"id": nuevo_id, **tarea.model_dump()}


@app.get("/tareas")
def listar_tareas():
    conn = get_connection()
    filas = conn.execute("SELECT * FROM tareas").fetchall()
    conn.close()
    return [dict(fila) for fila in filas ]

@app.delete("/tareas/{tarea_id}")
def borrar_tarea(tarea_id: int):
    conn = get_connection()
    cursor = conn.execute("DELETE FROM tareas WHERE id = ?", (tarea_id,)) 
    conn.commit()
    filas_borradas = cursor.rowcount
    conn.close()

    if filas_borradas == 0:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return {"mensaje": f"Tarea {tarea_id} eliminada"}

@app.put ("/tareas/{tarea_id}")
def actualizar_tarea(tarea_id: int, tarea: Tarea):
    conn = get_connection()
    cursor = conn.execute("UPDATE tareas SET titulo = ?, descripcion = ?, completada = ? WHERE id = ?", (tarea.titulo, tarea.descripcion, int(tarea.completada), tarea_id),)
    conn.commit()
    filas_actualizadas = cursor.rowcount
    conn.close()

    if filas_actualizadas == 0:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return {"mensaje": f"Tarea {tarea_id} actualizada", **tarea.model_dump()}


class Tarea_Parcial(BaseModel):
    titulo:str | None = None 
    descripcion: str | None = None 
    completada: bool | None = None 

@app.patch ("/tareas/{tarea_id}")
def modificar_tarea(tarea_id: int, cambios: Tarea_Parcial):
    datos =  cambios.model_dump(exclude_unset=True)
    if not datos:
        raise HTTPException(status_code=400, detail="No se actualizo ningun campo ^w^") 
    if "titulo" in datos and datos["titulo"] is None:
        raise HTTPException(status_code=400, detail="El titulo no puede ser NULL")
    if "completada" in datos:
        datos["completada"] = int(datos["completada"])
        columnas = ", ".join(f"{campo} = ?" for campo in datos)
        valores = list(datos.values()) + [tarea_id]

        conn = get_connection()
        cursor = conn.execute(f"UPDATE tareas SET {columnas} WHERE id = ?", valores)
        conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Tarea  no enontrada")
    fila = conn.execute("SELECT * FROM tareas WHERE id =?", (tarea_id,)).fetchone()
    conn.close()
    return dict(fila)

@app.get("/tareas/{tarea_id}")
def obtener_tarea(tarea_id: int):
    conn = get_connection()
    fila = conn.execute("SELECT * FROM tareas WHERE id = ?", (tarea_id,)).fetchone()
    conn.close()
    if fila is None: 
        raise HTTPException(status_code=404, detail= "Tarea no encontrada")
    return dict(fila)

class Tarea_Respuesta(BaseModel):
    id: int
    titulo: str
    descripcion: str | None = None 
    completada: bool 
    fecha: str | None = None 

@app.get ("/tareas/{tarea_id}", response_model=list[Tarea_Respuesta])
def listar_tarea():
    conn = get_connection()
    filas = conn.execute("SELECT * FROM tareas").fetchall()
    conn.close()
    return [dict(fila) for fila in filas]

@app.get ("/tareas/completadas", response_model= Tarea_Respuesta)
def obtener_tarea (tarea_id: int ):
    conn = get_connection()
    filas = conn.execute("SELECT * FROM tareas").fetchall()
    conn.close()
    return [dict(fila) for fila in filas]

@app.patch("/tareas/{tarea_id}/completada", response_model = Tarea_Respuesta)
def modificar_tarea(tarea_id: int, cambios: Tarea_Parcial):
      conn = get_connection()
      filas = conn.execute("SELECT * FROM tareas").fetchall()
      conn.close()
      return [dict(fila) for fila in filas]





