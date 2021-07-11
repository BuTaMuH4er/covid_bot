import config
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

engine_db = create_engine(f'postgres://{config.LOGIN_DB}:{config.PASS_DB}@{config.HOST_DB}/{config.NAME_DB}')
db_session = scoped_session(sessionmaker(bind=engine_db))

Base = declarative_base()
Base.query = db_session.query_property()