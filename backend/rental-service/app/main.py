from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from pydantic import BaseModel, Field
import os
from datetime import datetime, timezone
from typing import List, Optional

app = FastAPI(title="System Wypożyczalni Aut")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGO_URL = os.getenv("MONGO_URL", "mongodb://db:27017")
client = AsyncIOMotorClient(MONGO_URL)
db = client.wypozyczalnia


class RentalModel(BaseModel):
    car_id: str = Field(..., example="65f1a...") 
    customer_name: str = Field(..., example="Jan Kowalski")
    phone: str = Field(..., example="999888777")
    price: float
    rental_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    return_date: datetime = Field(..., example="2024-12-31T23:59:59")

def rental_helper(rental) -> dict:
    return {
        "id": str(rental["_id"]),
        "car_id": str(rental["car_id"]),
        "customer_name": rental["customer_name"],
        "phone": rental["phone"],
        "price": rental["price"],
        "rental_date": rental["rental_date"].isoformat(),
        "return_date": rental["return_date"].isoformat(),
    }


def calculate_total_price(start: datetime, end: datetime, p_day: float):
    s = start.replace(tzinfo=None)
    e = end.replace(tzinfo=None)

    delta = e - s
    days = delta.days

    if days <= 0:
        days = 1

    return float(days * p_day)

@app.post("/rentals", status_code=201)
async def create_rental(rental: RentalModel):
    if not ObjectId.is_valid(rental.car_id):
        raise HTTPException(status_code=400, detail="Nieprawidłowy format ID samochodu")

    car = await db.cars.find_one({"_id": ObjectId(rental.car_id)})
    if not car:
        raise HTTPException(status_code=404, detail="Nie znaleziono samochodu o podanym ID")

    if not car.get("available", True):
        raise HTTPException(status_code=400, detail="To auto jest obecnie wypożyczone")

    rental_dict = rental.model_dump()
    rental_dict["car_id"] = ObjectId(rental.car_id)

    rental_dict["price"] = calculate_total_price(
        rental.rental_date,
        rental.return_date,
        car.get("price_per_day", 0.0)
    )

    new_rental = await db.rentals.insert_one(rental_dict)

    await db.cars.update_one({"_id": ObjectId(rental.car_id)}, {"$set": {"available": False}})
    
    created_rental = await db.rentals.find_one({"_id": new_rental.inserted_id})
    return rental_helper(created_rental)

@app.get("/rentals")
async def get_all_rentals():
    rentals_cursor = db.rentals.find()
    rentals = await rentals_cursor.to_list(100)
    return [rental_helper(r) for r in rentals]

@app.get("/rentals/{id}")
async def get_rental(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Nieprawidłowy format ID wypożyczenia")
    
    rental = await db.rentals.find_one({"_id": ObjectId(id)})
    if rental:
        return rental_helper(rental)
    raise HTTPException(status_code=404, detail="Nie znaleziono wypożyczenia")

@app.post("/rentals/{id}/return")
async def return_car(id: str):

    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Nieprawidłowy format ID")
    
    rental = await db.rentals.find_one({"_id": ObjectId(id)})
    if not rental:
        raise HTTPException(status_code=404, detail="Nie znaleziono wypożyczenia")

    await db.cars.update_one({"_id": rental["car_id"]}, {"$set": {"available": True}})

    return {"message": "Auto zostało zwrócone i jest ponownie dostępne"}