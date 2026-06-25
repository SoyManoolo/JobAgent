from database import Base, engine

from models.oferta import Oferta

Base.metadata.create_all(engine)
