from pydantic import BaseModel
from typing import List, Optional

class MisionBase(BaseModel):
    titulo: str
    descripcion: str
    xp_recompensa: int

class MisionCreate(MisionBase):
    pass

class Mision(MisionBase):
    id: int

    class Config:
        from_attributes = True  # Cambio de 'orm_mode' a 'from_attributes'

class PersonajeBase(BaseModel):
    nombre: str

class PersonajeCreate(PersonajeBase):
    pass

class Personaje(PersonajeBase):
    id: int
    xp: int
    misiones: List[Mision] = []

    class Config:
        from_attributes = True  # Cambio de 'orm_mode' a 'from_attributes'
