from fastapi import Depends, FastAPI, Body, Form, Request
from fastapi.responses import HTMLResponse
#from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, declarative_base, sessionmaker
#-----------------
from random import randint
from sqlalchemy import Column, Integer, Sequence, String, create_engine 
from pydantic import BaseModel
from typing import Optional

Base = declarative_base()

class Item_pydantic(BaseModel):
    secret: str


class Item(Base):  
    __tablename__ = "items"

    id = Column(Integer, Sequence("items_id_sequence"), primary_key=True)
    secret = Column(String)


#DDB Engine definition
eng = create_engine("duckdb:///duck.db")

Base.metadata.create_all(eng)
SessionLocal = sessionmaker(eng)


#Session definition
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


# FastAPI code
app = FastAPI()


# Template folder
templates = Jinja2Templates(directory="templates")

#List of messages
RANDOM_MESSAGE_ARRAY = ["tem Carnaval aí?", "Melância", "bota o diuno no grupo"]


@app.get('/', response_class=HTMLResponse)
def read_root(request: Request, message: str= "This is Home. You will die."):
    context = {'request': request, 'message': message}
    return templates.TemplateResponse("index.html", context)


@app.get('/fragment', response_class=HTMLResponse)
def random_message(request: Request, message: str= "This is Home. You will die."):
    random_fragment = RANDOM_MESSAGE_ARRAY[randint(0,2)]
    message = message + " " + random_fragment
    context = {'request': request, 'message': message}
    return templates.TemplateResponse("message.html", context)


@app.get("/message", response_class=HTMLResponse)
def write_message(request: Request, message: Optional[str] = "WTf rofl"):
    context = {'request': request, 'message': message}
    return templates.TemplateResponse("index.html", context)


@app.get("/message/{message}", response_class=HTMLResponse)
def write_specific_message(request: Request, message: Optional[str] = None):
    context = {'request': request, 'message': message}
    return templates.TemplateResponse("message.html", context)


@app.get('/all')
def getItems(session: Session = Depends(get_session)):
    items = session.query(Item).all()
    if items == []:
        return "Item not found! you suck!"
    return items


@app.get('/id/{id}')
def getItem(id: int, session: Session = Depends(get_session)):
    item = session.query(Item).get(id)
    if item is None:
        return "Item not found! you suck!"
    return item


@app.post('/', response_class=HTMLResponse)
def addItem(request: Request, secret: str = Form(...), session = Depends(get_session)):
    item = Item(secret = secret)
    session.add(item)
    session.commit()
    session.refresh(item)
    context = {'request': request}
    return templates.TemplateResponse("form_response.html", context)
        
   
@app.put('/{id}')
def updateItem(id: int, item: Item_pydantic, session = Depends(get_session)):
    itemObject = session.query(Item).get(id)
    if itemObject is None:
        return "Item not found! you suck!"
    itemObject.secret = item.secret
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



