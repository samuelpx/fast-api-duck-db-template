
from fastapi import Depends, FastAPI, Body, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, declarative_base, sessionmaker
#-----------------
from sqlalchemy import Column, Integer, Sequence, String, create_engine, MetaData
from pydantic import BaseModel

Base = declarative_base()

class Item_pydantic(BaseModel):
    task: str


class Item(Base):  # type: ignore
    __tablename__ = "items"

    id = Column(Integer, Sequence("items_id_sequence"), primary_key=True)
    task = Column(String)


eng = create_engine("duckdb:///duck.db")

Base.metadata.create_all(eng)
SessionLocal = sessionmaker(eng)
#------------ DUCKDB session stuff
# session = Session(bind=eng)
# 
# session.add(FakeModel(name="Frank"))
# session.commit()

# frank = session.query(FakeModel).one()

#----------- MAIN.PY

def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

# FastAPI code
app = FastAPI()


@app.get('/')
def read_root():
    return {"Hello": "World"}

@app.get('/all')
def getItems(session: Session = Depends(get_session)):
    items = session.query(Item).all()
    if items == []:
        return "Item not found! you suck!"
    return items

@app.get('/{id}')
def getItem(id: int, session: Session = Depends(get_session)):
    item = session.query(Item).get(id)
    if item is None:
        return "Item not found! you suck!"
    return item

# OPTION #1 - NO PYDANTIC
#@app.post("/")
#def addItem(task: str):
#    newId = len(fake_database.keys()) + 1
#    fake_database[newId] = {'task':task}
#    
#    return fake_database

# OPTION #2 - USING PYDANTIC
@app.post('/')
def addItem(item: Item_pydantic, session = Depends(get_session)):
    item = Item(task = item.task)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item
        
# OPTION #3 - 
#@app.post('/')
#def addItem(body = Body()):
#    newId = len(fake_database.keys()) + 1
#    fake_database[newId] = {'task': body['task']}
#    return fake_database
   
@app.put('/{id}')
def updateItem(id: int, item: Item_pydantic, session = Depends(get_session)):
    itemObject = session.query(Item).get(id)
    if itemObject is None:
        return "Item not found! you suck!"
    itemObject.task = item.task
    session.commit()
    return itemObject

@app.delete('/{id}')
def deleteItem(id: int, session = Depends(get_session)):
    itemObject = session.query(Item).get(id)
    if itemObject is None:
        return "Item not found! you suck!"
    session.delete(itemObject)
    session.commit()
    session.close()
    return 'Item was deleted'



