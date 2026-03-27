from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship
from pydantic import BaseModel
from datetime import datetime, timezone

# Database Setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./crm.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    tag = Column(String, index=True)
    date_of_contact = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    email = Column(String, unique=True, index=True)
    telephone = Column(String)
    correspondences = relationship("Correspondence", back_populates="client")

class Correspondence(Base):
    __tablename__ = "correspondences"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    message = Column(Text)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    sender = Column(String) # 'user' or 'client'
    client = relationship("Client", back_populates="correspondences")

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Schemas
class ClientCreate(BaseModel):
    name: str
    tag: str
    email: str
    telephone: str

class CorrespondenceCreate(BaseModel):
    message: str
    sender: str

# Routes
@app.post("/clients/")
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    db_client = Client(**client.model_dump())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

@app.get("/clients/")
def get_clients(db: Session = Depends(get_db)):
    return db.query(Client).all()

@app.post("/clients/{client_id}/correspondence/")
def add_correspondence(client_id: int, corr: CorrespondenceCreate, db: Session = Depends(get_db)):
    db_client = db.query(Client).filter(Client.id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    db_corr = Correspondence(client_id=client_id, **corr.model_dump())
    db.add(db_corr)
    db.commit()
    db.refresh(db_corr)
    return db_corr

@app.get("/clients/{client_id}/correspondence/")
def get_correspondence(client_id: int, db: Session = Depends(get_db)):
    return db.query(Correspondence).filter(Correspondence.client_id == client_id).all()
