from fastapi import Depends, FastAPI, Body, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import schemas
import models

from database import Base, engine, SessionLocal
from sqlalchemy.orm import Session


#Initiating DB 
Base.metadata.create_all(engine)

def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


# FastAPI code
app = FastAPI()

fake_database = {
        1:{'task':'Clean Car'},
        2:{'task':'write blog'},
        3:{'task':'start stream'}
    }

@app.get('/')
def read_root():
    return {"Hello": "World"}

@app.get('/all')
def getItems(session: Session = Depends(get_session)):
    items = session.query(models.Item).all()
    return items

@app.get('/{id}')
def getItem(id: int, session: Session = Depends(get_session)):
    item = session.query(models.Item).get(id)
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
def addItem(item: schemas.Item, session = Depends(get_session)):
    item = models.Item(task = item.task)
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
def updateItem(id: int, item: schemas.Item, session = Depends(get_session)):
    itemObject = session.query(models.Item).get(id)
    itemObject.task = item.task
    session.commit()
    return itemObject

@app.delete('/{id}')
def deleteItem(id: int, session = Depends(get_session)):
    itemObject = session.query(models.Item).get(id)
    session.delete(itemObject)
    session.commit()
    session.close()
    return 'Item was deleted'



