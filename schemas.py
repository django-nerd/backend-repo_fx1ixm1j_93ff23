"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Divine Flavours: Cake orders
class CakeOrder(BaseModel):
    """
    Cake orders placed by customers. Collection name: "cakeorder".
    Delivery price is included in total price.
    Layers are only applicable to medium (2) and large (3) cakes.
    """
    customer_name: str = Field(..., description="Customer full name")
    phone: str = Field(..., description="Contact phone number")
    size: Literal['small', 'medium', 'large'] = Field(..., description="Cake size")
    layers: Optional[int] = Field(None, ge=1, le=3, description="Number of layers (medium=2, large=3)")
    notes: Optional[str] = Field(None, description="Additional notes or instructions")
    reference_image_path: Optional[str] = Field(None, description="Server path to uploaded reference image")
    price_omr: float = Field(..., ge=0, description="Total price in OMR, delivery included")
