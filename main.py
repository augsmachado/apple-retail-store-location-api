import os

from typing import Annotated, Union
from datetime import datetime

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Json

from deta import Deta

from dotenv import load_dotenv


# Initalize constants
SMALL_ALLOWED = 3

# Initialize environment variables
load_dotenv()
DETA_PROJECT_KEY = os.getenv("DETA_PROJECT_KEY")

# Initialize with a Project Key
deta = Deta(DETA_PROJECT_KEY)

# This how to connect to or create a database.
db = deta.Base("stores")

# Initialize FastAPI server
app = FastAPI()


# Store base model
class Store(BaseModel):
    country: str
    state: str
    city: str
    address: str
    number: int
    neighborhood: str
    zipcode: str
    phone: Union[str, None] = None
    latitude: Union[float, None] = None
    longitude: Union[float, None] = None
    link: Union[str, None] = None


# get api status
@app.get("/status")
def read_root():
    return {
        "msg": "Current API status",
        "name": "apple-stores-api",
        "environment": "production",
        "version": "1.0.0",
        "uptime": datetime.now(),
    }


# get all stores
@app.get("/stores")
def get_all_stores():
    # to do: add support to pagination and queries
    return db.fetch(query=None, limit=1000, last=None)


# request specific store details
@app.get("/stores/{store_id}")
def get_store_details(store_id: str):
    return db.get(store_id)


# create new store
@app.post("/stores")
def post_new_store(store: Store):
    if len(store.country) <= SMALL_ALLOWED:
        raise HTTPException(
            status_code=400, detail=f"[COUNTRY] Name {store.country} is too short"
        )

    if len(store.state) <= SMALL_ALLOWED:
        raise HTTPException(
            status_code=400, detail=f"[STATE] Name {store.state} is too short"
        )

    if len(store.city) <= SMALL_ALLOWED:
        raise HTTPException(
            status_code=400, detail=f"[CITY] Name {store.city} is too short"
        )

    if len(store.address) <= SMALL_ALLOWED:
        raise HTTPException(
            status_code=400, detail=f"[ADDRESS] {store.address} is too short"
        )

    # To do: add verification to number passed
    # if store.number > 0 and store.number is not None:
    #    raise HTTPException(status_code=400, detail="${store.number} is not a number")

    if len(store.neighborhood) <= SMALL_ALLOWED:
        raise HTTPException(
            status_code=400, detail=f"[NEIGHBORHOOD] {store.neighborhood} is too short"
        )

    if len(store.zipcode) <= SMALL_ALLOWED:
        raise HTTPException(
            status_code=400, detail=f"[ZIPCODE] {store.zipcode} is too short"
        )

    if len(store.link) <= SMALL_ALLOWED:
        raise HTTPException(status_code=400, detail=f"[LINK] {store.link} is too short")

    phone = store.phone if store.phone is not None else None

    data = {
        "country": store.country.upper(),
        "state": store.state.upper(),
        "city": store.city.upper(),
        "address": store.address.upper(),
        "number": store.number,
        "neighborhood": store.neighborhood.upper(),
        "zipcode": store.zipcode,
        "phone": phone,
        "latitude": store.latitude,
        "longitude": store.longitude,
        "link": store.link,
        "created_at": str(datetime.utcnow()),
        "updated_at": str(datetime.utcnow()),
    }

    return db.put(data)


# update store
@app.put("/stores/{store_id}")
def update_store(store_id: str, data: dict):
    # add updated_at
    res = db.update(data, store_id)

    if res is not None:
        raise HTTPException(status_code=400, detail="Invalid to update")

    return db.get(store_id)


# delete store
@app.delete("/stores/{store_id}")
def delete_store(store_id: str):
    db.delete(store_id)

    res = db.get(store_id)

    if res is None:
        return {"msg": f"Store {store_id} is deleted"}
