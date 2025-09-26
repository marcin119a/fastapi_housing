from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from functools import lru_cache

import models
from database import engine, SessionLocal
from ml import predict_price

# Utwórz tabele
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Housing API")

# Dependency – sesja DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Root
@app.get("/")
def root():
    return {"message": "API do mieszkań we Wrocławiu"}

# Dodawanie oferty
@app.post("/offers/", response_model=models.Offer)
def create_offer(offer: models.Offer, db: Session = Depends(get_db)):
    db_offer = models.OfferDB(**offer.dict())
    db.add(db_offer)
    db.commit()
    db.refresh(db_offer)
    return db_offer

# Pobieranie wszystkich ofert
@app.get("/offers/")
@lru_cache(maxsize=32)  # cache’owanie wyników
def read_offers(db: Session = Depends(get_db)):
    return db.query(models.OfferDB).all()

# Predykcja ceny
@app.post("/predict/")
def predict(offer: models.OfferCreate):
    predicted_price = predict_price(offer.area_m2, offer.rooms)
    return {"predicted_price": round(predicted_price, 2)}