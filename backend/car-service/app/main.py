from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from pydantic import BaseModel, Field
from typing import Optional
import os

app = FastAPI(title="System Wypożyczalni Aut - Car Service")

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

class CarModel(BaseModel):
    brand: str = Field(..., example="Toyota")
    model: str = Field(..., example="Corolla")
    year: int = Field(..., example=2022)
    version: str = Field(..., example="Hybrid Executive")
    capacity: str = Field(..., example="1798 cm3")
    power: int = Field(..., example=122, description="Moc w KM")
    fuel: str = Field(..., example="Benzyna+Elektryczny")
    vin: str = Field(..., example="JTNB1234567890")
    price_per_day: float = Field(..., example=199.00)
    regNumber: str = Field(..., example="WA12345")
    available: bool = Field(default=True)

# --- HELPER ---
def car_helper(car) -> dict:
    return {
        "id": str(car["_id"]),
        "brand": car.get("brand"),
        "model": car.get("model"),
        "year": car.get("year"),
        "version": car.get("version"),
        "capacity": car.get("capacity"),
        "power": car.get("power"),
        "fuel": car.get("fuel"),
        "vin": car.get("vin"),
        "price_per_day": car.get("price_per_day"),
        "regNumber": car.get("regNumber"),
        "available": car.get("available", True)
    }

@app.get("/")
def read_root():
    return {"status": "Car Service is running"}

@app.get("/cars")
async def get_cars():
    cars_cursor = db.cars.find()
    cars = await cars_cursor.to_list(100)
    return [car_helper(car) for car in cars]

@app.get("/cars/{id}")
async def get_car(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Nieprawidłowy format ID")
    
    car = await db.cars.find_one({"_id": ObjectId(id)})
    if car:
        return car_helper(car)
    raise HTTPException(status_code=404, detail="Nie znaleziono samochodu")

@app.post("/cars", status_code=201)
async def create_car(car: CarModel):
    car_dict = car.model_dump() 
    new_car = await db.cars.insert_one(car_dict)
    created_car = await db.cars.find_one({"_id": new_car.inserted_id})
    return car_helper(created_car)

@app.delete("/cars/{id}")
async def delete_car(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Nieprawidłowy format ID")
    
    delete_result = await db.cars.delete_one({"_id": ObjectId(id)})
    if delete_result.deleted_count == 1:
        return {"message": "Samochód został usunięty"}
    raise HTTPException(status_code=404, detail="Nie znaleziono samochodu")