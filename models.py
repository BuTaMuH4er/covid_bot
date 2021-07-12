from sqlalchemy import Column, String, BOOLEAN
from db import Base, engine_db

class User(Base):
    __tablename__ = 'users'
    chat_id = Column(String, primary_key=True)
    name = Column(String)
    subscribe = Column(BOOLEAN)
    send_info = Column(BOOLEAN)

    def __repr__(self):
        return f'{self.name} {self.chat_id} {self.subscribe}'


class Vaccine(Base):
    __tablename__ = 'vaccine'
    vaccine = Column(String, primary_key=True)
    info_availability = Column(String, nullable=False)

    def __repr__(self):
        return f'{self.vaccine} : \n {self.info_availability}'

if __name__ == '__main__':
    Base.metadata.create_all(bind=engine_db)