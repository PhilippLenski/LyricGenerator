import requests
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, init_db, Address, Poem
from model import generate_poem

# FastAPI-Instanz erstellen
app = FastAPI()

# Datenbank initialisieren
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency für die Datenbank-Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic-Modelle für API-Requests
class AddressCreate(BaseModel):
    street: str
    house_number: str
    city: str
    country: str

### 📌 1️⃣ Adresse speichern + Gedicht generieren ###
@app.post("/address/")
def add_address(data: AddressCreate, db: Session = Depends(get_db)):
    # Prüfen, ob die Adresse bereits existiert
    existing_address = db.query(Address).filter(
        Address.street == data.street,
        Address.house_number == data.house_number,
        Address.city == data.city,
        Address.country == data.country
    ).first()

    if existing_address:
        raise HTTPException(status_code=400, detail="Adresse existiert bereits!")

    # Prüfen, ob für den Wohnort bereits ein Gedicht existiert
    poem = db.query(Poem).filter(Poem.city == data.city).first()
    
    if not poem:
        poem_text = generate_poem(data.city)  # 🔥 Gedicht generieren
        poem = Poem(city=data.city, text=poem_text)
        db.add(poem)
        db.commit()
        db.refresh(poem)

    # Adresse speichern
    new_address = Address(
        street=data.street, 
        house_number=data.house_number, 
        city=data.city, 
        country=data.country,
        poem_id=poem.id  
    )
    db.add(new_address)
    db.commit()
    db.refresh(new_address)

    return {
        "message": "Adresse gespeichert",
        "poem": poem.text  
    }

### 📌 2️⃣ Gespeicherte Adressen abrufen ###
@app.get("/addresses/")
def get_addresses(db: Session = Depends(get_db)):
    addresses = db.query(Address).all()
    return [
        {
            "id": a.id,
            "street": a.street,
            "house_number": a.house_number,
            "city": a.city,
            "country": a.country
        }
        for a in addresses
    ]

### 📌 3️⃣ Adresse & Gedicht abrufen ###
@app.get("/address/{city}")
def get_address(city: str, db: Session = Depends(get_db)):
    address = db.query(Address).filter(Address.city == city).first()
    if not address:
        raise HTTPException(status_code=404, detail="Adresse nicht gefunden")
    
    poem_text = address.poem.text if address.poem else "Kein Gedicht vorhanden"
    
    return {
        "street": address.street,
        "house_number": address.house_number,
        "city": address.city,
        "country": address.country,
        "poem": poem_text
    }

### 📌 4️⃣ Adresse & Gedicht löschen ###
@app.delete("/address/{city}")
def delete_address(city: str, db: Session = Depends(get_db)):
    address = db.query(Address).filter(Address.city == city).first()
    if not address:
        raise HTTPException(status_code=404, detail="Adresse nicht gefunden")

    db.delete(address)
    db.commit()
    return {"message": f"Adresse {city} wurde gelöscht"}

@app.put("/address/{city}")
def update_poem(city: str, db: Session = Depends(get_db)):
    # 🔹 Prüfen, ob für die Stadt eine Adresse existiert
    address = db.query(Address).filter(Address.city == city).first()
    if not address:
        raise HTTPException(status_code=404, detail="Adresse nicht gefunden")

    # 🔹 Prüfen, ob für die Stadt bereits ein Gedicht existiert
    poem = db.query(Poem).filter(Poem.city == city).first()
    new_poem_text = generate_poem(city)  # 🔥 Neues Gedicht generieren

    if poem:
        # 🔹 Gedicht aktualisieren
        poem.text = new_poem_text
    else:
        # 🔹 Falls kein Gedicht existiert, erstelle ein neues
        poem = Poem(city=city, text=new_poem_text)
        db.add(poem)
        db.commit()
        db.refresh(poem)

    # 🔹 Die Adresse mit dem neuen Gedicht verknüpfen
    address.poem_id = poem.id
    db.commit()

    return {"city": city, "updated_poem": poem.text}

# 📌 Wikipedia-Link für eine Stadt abrufen
@app.get("/wikipedia/{city}")
def get_wikipedia_link(city: str):
    url = f"https://de.wikipedia.org/api/rest_v1/page/summary/{city}"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {"title": data["title"], "link": data["content_urls"]["desktop"]["page"]}
    else:
        return {"error": "Kein Wikipedia-Eintrag gefunden"}