import configparser
import pathlib

from fastapi import HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from src.confg.config import settings

# Read config file
file_config = pathlib.Path(__file__).parent.parent.joinpath('confg/config.ini')
config = configparser.ConfigParser()
config.read(file_config)



# Create DB URI
URI = settings.sqlalchemy_database_url


# Create engine and session
engine = create_engine(URI, echo=True)
DBSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency
def get_db():
    db = DBSession()
    try:
        yield db
    except SQLAlchemyError as err:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    finally:
        db.close()
