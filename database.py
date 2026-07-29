from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine
from pathlib import Path


class Base(DeclarativeBase):
    pass


DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(exist_ok=True)

engine = create_engine(f"sqlite:///{DATA_DIR / 'jobagent.sqlite'}", echo=False)

SessionLocal = sessionmaker(autoflush=False, bind=engine, autocommit=False)
