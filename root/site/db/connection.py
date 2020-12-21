from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from root.core import DB


def get_engine(db_name: str,  # разрешены названия из config.DB['names']
               ) -> create_engine:
    return create_engine(f"mysql+pymysql://{DB['user']}:{DB['password']}@{DB['host']}/{DB['names'][db_name]}")


def get_session(db_name: str,  # разрешены названия из config.DB['names']
                ) -> Session:
    _Session = sessionmaker(bind=get_engine(db_name))
    return _Session()
