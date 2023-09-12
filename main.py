import os

from datetime import datetime, timezone
from typing import Union

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

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


# The above class is a subclass of BaseModel and represents a store.
class Store(BaseModel):
    code_name: str
    country: str
    city: str
    address: str
    number: int
    phone: Union[str, None] = None
    latitude: Union[float, None] = None
    longitude: Union[float, None] = None
    link: str


# Validation methods
def small_allowed(value):
    return len(value) > SMALL_ALLOWED


# `@app.get("/status")` is a decorator in FastAPI that defines a route for handling GET requests to
# the "/status" endpoint. When a GET request is made to this endpoint, the function immediately below
# the decorator (`def read_root():`) will be executed. This function is responsible for returning the
# current status of the API, including the name, environment, version, and uptime.
@app.get("/api/v1/status")
def read_root():
    return {
        "msg": "Current API status",
        "name": "apple-stores-api",
        "environment": "production",
        "version": "1.1.5",
        "uptime": datetime.now(),
    }


# `@app.get("/stores")` is a decorator in FastAPI that defines a route for handling GET requests to
# the "/stores" endpoint. When a GET request is made to this endpoint, the function immediately below
# the decorator (`def get_all_stores():`) will be executed. This function is responsible for
# retrieving and returning all stores from the database.
@app.get("/api/v1/stores")
def get_all_stores():
    # to do: add support to pagination and queries

    return db.fetch(query=None, limit=1000, last=None)


@app.get("/api/v1/stores-by-country")
def get_stores_by_country(country: str):
    q = {"country": country.upper()}

    return db.fetch(query=q, limit=1000, last=None)


# `@app.get("/stores/{store_id}")` is a decorator in FastAPI that defines a route for handling GET
# requests to the "/stores/{store_id}" endpoint. When a GET request is made to this endpoint, the
# function immediately below the decorator (`def get_store_details(store_id: str):`) will be executed.
# This function is responsible for retrieving and returning the details of a specific store from the
# database based on the provided `store_id` parameter.
@app.get("/api/v1/stores/{store_id}")
def get_store_details(store_id: str):
    res = db.get(store_id)

    try:
        if res is not None:
            return res
    except:
        raise HTTPException(status_code=404, detail="Store not found")


# `@app.post("/stores")` is a decorator in FastAPI that defines a route for handling POST requests to
# the "/stores" endpoint. When a POST request is made to this endpoint, the function immediately below
# the decorator (`def post_new_store(store: Store):`) will be executed. This function is responsible
# for creating a new store in the database based on the provided store data in the request body.
@app.post("/stores")
def post_new_store(store: Store):
    if len(store.code_name) <= SMALL_ALLOWED:
        raise HTTPException(
            status_code=400, detail=f"[CODE_NAME] Value {store.code_name} is too short"
        )

    if len(store.country) <= SMALL_ALLOWED:
        raise HTTPException(
            status_code=400, detail=f"[COUNTRY] Value {store.country} is too short"
        )

    if len(store.city) <= SMALL_ALLOWED:
        raise HTTPException(
            status_code=400, detail=f"[CITY] Value {store.city} is too short"
        )

    if len(store.address) <= SMALL_ALLOWED:
        raise HTTPException(
            status_code=400, detail=f"[ADDRESS] Value {store.address} is too short"
        )

    number = max(store.number, 0)

    phone = store.phone if store.phone is not None else None

    latitude = store.latitude if store.latitude is not None else None

    longitude = store.longitude if store.longitude is not None else None

    if len(store.link) <= SMALL_ALLOWED:
        raise HTTPException(
            status_code=400, detail=f"[LINK] Value {store.link} is too short"
        )

    data = {
        "code_name": store.code_name.upper(),
        "country": store.country.upper(),
        "city": store.city.upper(),
        "address": store.address.upper(),
        "number": number,
        "phone": phone,
        "latitude": latitude,
        "longitude": longitude,
        "link": store.link,
        "created_at": str(datetime.now(timezone.utc)),
        "updated_at": str(datetime.now(timezone.utc)),
    }

    return db.put(data)


# `@app.put("/stores/{store_id}")` is a decorator in FastAPI that defines a route for handling PUT
# requests to the "/stores/{store_id}" endpoint. When a PUT request is made to this endpoint, the
# function immediately below the decorator (`def update_store(store_id: str, store: dict):`) will be
# executed. This function is responsible for updating the details of a specific store in the database
# based on the provided `store_id` parameter and the updated store data in the request body.
@app.put("/stores/{store_id}")
def update_store(store_id: str, store: dict):
    res = db.update(store, store_id)

    req = db.get(store_id)
    data = {
        "code_name": req["code_name"].upper(),
        "country": req["country"].upper(),
        "city": req["city"].upper(),
        "address": req["address"].upper(),
        "number": req["number"],
        "phone": req["phone"],
        "latitude": req["latitude"],
        "longitude": req["longitude"],
        "link": req["link"],
        "created_at": req["created_at"],
        "updated_at": str(datetime.now(timezone.utc)),
    }
    res = db.update(data, store_id)

    if res is not None:
        raise HTTPException(status_code=400, detail="Invalid to update")

    return db.get(store_id)


# `@app.delete("/stores/{store_id}")` is a decorator in FastAPI that defines a route for handling
# DELETE requests to the "/stores/{store_id}" endpoint. When a DELETE request is made to this
# endpoint, the function immediately below the decorator (`def delete_store(store_id: str):`) will be
# executed. This function is responsible for deleting a specific store from the database based on the
# provided `store_id` parameter.
@app.delete("/stores/{store_id}")
def delete_store(store_id: str):
    db.delete(store_id)
    res = db.get(store_id)

    if res is None:
        return {"msg": f"Store {store_id} is deleted"}
