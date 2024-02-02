from sqlalchemy import Column, Integer, String, Sequence
from database import Base

class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, Sequence("item_id_sequence"), primary_key=True)
    task = Column(String)
