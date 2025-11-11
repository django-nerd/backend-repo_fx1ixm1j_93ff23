import os
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import CakeOrder

app = FastAPI(title="Divine Flavours API", description="Custom cakes ordering API for Divine Flavours, Oman")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Divine Flavours backend is running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# Helper for price calculation (delivery included)
SIZE_BASE_PRICES = {
    "small": 8.0,   # OMR
    "medium": 12.0, # OMR
    "large": 16.0   # OMR
}
DELIVERY_INCLUSIVE = 0.0  # Delivery price included in base


def calculate_price(size: str) -> float:
    if size not in SIZE_BASE_PRICES:
        raise HTTPException(status_code=400, detail="Invalid size")
    return SIZE_BASE_PRICES[size] + DELIVERY_INCLUSIVE


# Create order with optional image upload
@app.post("/orders")
async def create_order(
    customer_name: str = Form(...),
    phone: str = Form(...),
    size: str = Form(...),
    layers: Optional[int] = Form(None),
    notes: Optional[str] = Form(None),
    reference_image: Optional[UploadFile] = File(None)
):
    size = size.lower()
    if size not in ("small", "medium", "large"):
        raise HTTPException(status_code=400, detail="Size must be small, medium, or large")

    # Validate layers rules
    if size == "small":
        layers_value = None  # not applicable
    elif size == "medium":
        if layers not in (None, 2):
            raise HTTPException(status_code=400, detail="Medium cakes must have exactly 2 layers")
        layers_value = 2
    else:  # large
        if layers not in (None, 3):
            raise HTTPException(status_code=400, detail="Large cakes must have exactly 3 layers")
        layers_value = 3

    image_path = None
    if reference_image is not None:
        uploads_dir = "uploads"
        os.makedirs(uploads_dir, exist_ok=True)
        filename = reference_image.filename
        # Make safe filename
        base, ext = os.path.splitext(filename)
        safe_base = base.replace(' ', '_')[:50]
        final_name = f"{safe_base}_{ObjectId()}{ext}"
        file_path = os.path.join(uploads_dir, final_name)
        with open(file_path, 'wb') as f:
            f.write(await reference_image.read())
        image_path = f"/{file_path}"

    price = calculate_price(size)

    order = CakeOrder(
        customer_name=customer_name,
        phone=phone,
        size=size, 
        layers=layers_value,
        notes=notes,
        reference_image_path=image_path,
        price_omr=price
    )

    inserted_id = create_document("cakeorder", order)
    return {"id": inserted_id, "message": "Order created", "price_omr": price}


# List orders (latest 25)
@app.get("/orders")
def list_orders(limit: int = 25):
    docs = get_documents("cakeorder", {}, limit=limit)
    # Convert ObjectId and datetime to strings
    for d in docs:
        if "_id" in d:
            d["id"] = str(d.pop("_id"))
        for key in ("created_at", "updated_at"):
            if key in d:
                d[key] = str(d[key])
    return {"orders": docs}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
