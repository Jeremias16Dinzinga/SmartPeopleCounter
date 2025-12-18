from fastapi import Depends

from sqlalchemy.orm import Session
from database import SessionLocal
from models import PeopleCount

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/count")
def save_count(count: int, db: Session = Depends(get_db)):
    record = PeopleCount(count=count)
    db.add(record)
    db.commit()
    return {"message": "Contagem salva com sucesso"}