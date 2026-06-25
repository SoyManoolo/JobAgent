from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine


class Base(DeclarativeBase):
    pass


engine = create_engine("sqlite:///jobagent.sqlite", echo=True)

SessionLocal = sessionmaker(autoflush=False, bind=engine, autocommit=False)
