from fastapi import FastAPI, Form
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String
import databases
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

DATABASE_URL = "postgresql+asyncpg://postgres:Millonarios1@localhost/forms_qhronus"

database = databases.Database(DATABASE_URL)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    empresa = Column(String, index=True)
    correo = Column(String, index=True)
    celular = Column(String, index=True)

engine = create_async_engine(
    DATABASE_URL, echo=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

app = FastAPI()

class UserCreate(BaseModel):
    nombre: str
    empresa: str
    correo: str
    celular: str

@app.on_event("startup")
async def startup():
    await database.connect()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.post("/submit")
async def create_user(
    nombre: str = Form(...),
    empresa: str = Form(...),
    correo: str = Form(...),
    celular: str = Form(...)
):
    query = User.__table__.insert().values(nombre=nombre, empresa=empresa, correo=correo, celular=celular)
    last_record_id = await database.execute(query)
    return {"id": last_record_id}

# Sirve el archivo HTML
@app.get("/", response_class=HTMLResponse)
async def get_form():
    with open("static/form.html") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

# Servir archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")