"""
La API está construida con FastAPI en el archivo main.py. Aqui se definen los endpoints que permiten
interactuar con el sistema RPG de manera RESTful.
"""
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import Personaje, Mision
from cola import Cola

app = FastAPI()

Base.metadata.create_all(bind=engine)
colas_personaje = {}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/personajes")
def crear_personaje(nombre: str, db: Session = Depends(get_db)):
    personaje = Personaje(nombre=nombre)
    db.add(personaje)
    db.commit()
    db.refresh(personaje)
    colas_personaje[personaje.id] = Cola()
    return personaje

@app.post("/misiones")
def crear_mision(descripcion: str, xp: int, db: Session = Depends(get_db)):
    mision = Mision(descripcion=descripcion, xp=xp)
    db.add(mision)
    db.commit()
    db.refresh(mision)
    return mision

@app.post("/personajes/{personaje_id}/aceptar/{mision_id}")
def aceptar_mision(personaje_id: int, mision_id: int, db: Session = Depends(get_db)):
    personaje = db.query(Personaje).filter(Personaje.id == personaje_id).first()
    mision = db.query(Mision).filter(Mision.id == mision_id).first()

    if not personaje or not mision:
        raise HTTPException(status_code=404, detail="Personaje o misión no encontrados")

    if personaje_id not in colas_personaje:
        colas_personaje[personaje_id] = Cola()

   
    colas_personaje[personaje_id].enqueue(mision.id)

    return {"mensaje": "Misión aceptada"}


@app.post("/personajes/{personaje_id}/completar")
def completar_mision(personaje_id: int, db: Session = Depends(get_db)):
    personaje = db.query(Personaje).filter(Personaje.id == personaje_id).first()
    if personaje is None:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")

    if personaje_id not in colas_personaje or colas_personaje[personaje_id].is_empty():
        raise HTTPException(status_code=400, detail="No hay misiones para completar")

    mision_id = colas_personaje[personaje_id].dequeue()
    if isinstance(mision_id, Mision):  
        mision_id = mision_id.id

    mision = db.query(Mision).filter(Mision.id == mision_id).first()
    if mision is None:
        raise HTTPException(status_code=404, detail="Misión no encontrada")

    personaje.xp += mision.xp
    db.commit()
    db.refresh(personaje)

    return {"mensaje": "Misión completada", "xp_actual": personaje.xp}

@app.get("/personajes/{personaje_id}/misiones")
def listar_misiones(personaje_id: int):
    if personaje_id not in colas_personaje:
        raise HTTPException(status_code=404, detail="Cola de personaje no encontrada")
    misiones = [m.descripcion for m in colas_personaje[personaje_id].items]
    return {"misiones_en_orden": misiones}