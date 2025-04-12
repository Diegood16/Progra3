from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models, schemas
from cola import ColaDeMisiones
from typing import List

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
colas = {}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def restaurar_colas():
    db = SessionLocal()
    personajes = db.query(models.Personaje).all()
    for personaje in personajes:
        colas[personaje.id] = ColaDeMisiones()
        for mision in personaje.misiones:
            colas[personaje.id].enqueue(mision)
    db.close()

# Crear personaje
@app.post("/personajes", response_model=schemas.Personaje)
def crear_personaje(personaje: schemas.PersonajeCreate, db: Session = Depends(get_db)):
    db_personaje = models.Personaje(nombre=personaje.nombre)
    db.add(db_personaje)
    db.commit()
    db.refresh(db_personaje)
    colas[db_personaje.id] = ColaDeMisiones()
    return db_personaje

# Crear misión
@app.post("/misiones", response_model=schemas.Mision)
def crear_mision(mision: schemas.MisionCreate, db: Session = Depends(get_db)):
    db_mision = models.Mision(**mision.dict())
    db.add(db_mision)
    db.commit()
    db.refresh(db_mision)
    return db_mision

# Aceptar misión
@app.post("/personajes/{personaje_id}/misiones/{mision_id}")
def aceptar_mision(personaje_id: int, mision_id: int, db: Session = Depends(get_db)):
    personaje = db.query(models.Personaje).filter_by(id=personaje_id).first()
    mision = db.query(models.Mision).filter_by(id=mision_id).first()
    if not personaje or not mision:
        raise HTTPException(status_code=404, detail="Personaje o misión no encontrados")
    if mision in personaje.misiones:
        return {"mensaje": "Esta misión ya fue aceptada por este personaje."}
    personaje.misiones.append(mision)
    db.commit()
    if personaje_id not in colas:
        colas[personaje_id] = ColaDeMisiones()
    colas[personaje_id].enqueue(mision)
    return {"mensaje": "Misión aceptada correctamente"}

@app.post("/{personaje_id}/completar")
def completar_mision(personaje_id: int, db: Session = Depends(get_db)):
    personaje = db.query(models.Personaje).filter_by(id=personaje_id).first()
    if not personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")

    if personaje_id not in colas or colas[personaje_id].is_empty():
        raise HTTPException(status_code=400, detail="No hay misiones por completar")

    # Obtener la misión de la cola
    mision = colas[personaje_id].dequeue()

    # Reobtener la misión desde la base de datos (evitar DetachedInstanceError)
    mision_bd = db.query(models.Mision).filter_by(id=mision.id).first()

    if not mision_bd:
        raise HTTPException(status_code=404, detail="Misión no encontrada en base de datos")

   
    personaje.xp += mision_bd.xp_recompensa

    # Remover la misión completada por ID
    personaje.misiones = [m for m in personaje.misiones if m.id != mision.id]

    db.commit()
    db.refresh(personaje) 

    return {"mensaje": f"Misión completada. XP ganada: {mision_bd.xp_recompensa}"}

@app.get("/personajes/{personaje_id}/misiones", response_model=List[schemas.Mision])
def listar_misiones(personaje_id: int, db: Session = Depends(get_db)):
    personaje = db.query(models.Personaje).filter_by(id=personaje_id).first()
    
    if not personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")

    
    misiones = personaje.misiones #Consulta las misiones del pj directa a la database
    
    return [schemas.Mision.from_orm(m) for m in misiones]
