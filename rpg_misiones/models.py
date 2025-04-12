# models.py
from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

personaje_mision = Table(
    'personaje_mision',
    Base.metadata,
    Column('personaje_id', ForeignKey('personajes.id'), primary_key=True),
    Column('mision_id', ForeignKey('misiones.id'), primary_key=True),
   
)

class Personaje(Base):
    __tablename__ = 'personajes'

    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    xp = Column(Integer, default=0)
    misiones = relationship("Mision", secondary=personaje_mision)

class Mision(Base):
    __tablename__ = 'misiones'
    

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)
    descripcion = Column(String)
    xp_recompensa = Column(Integer)