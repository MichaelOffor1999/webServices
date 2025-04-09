import requests
from fastapi import FastAPI, HTTPException, Query
from pymongo import MongoClient
from pydantic import BaseModel


app = FastAPI()

# Connect to MongoDB (use the internal Docker hostname if needed)
client = MongoClient("mongodb://mongo:27017/")  # "mongo" is the Docker service name
db = client["inventory_db"]
collection = db["products"]

@app.get("/getAll")
def get_all_products():
    products = list(collection.find({}, {"_id": 0}))
    return {"products": products}


@app.get("/getSingleProduct")
def get_single_product(product_id: str):
    product = collection.find_one({"ProductID": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# Pydantic model for input validation
class Product(BaseModel):
    ProductID: str
    Name: str
    UnitPrice: float
    StockQuantity: int
    Description: str

@app.post("/addNew")
def add_new_product(product: Product):
    # Check if ProductID already exists
    existing = collection.find_one({"ProductID": product.ProductID})
    if existing:
        raise HTTPException(status_code=400, detail="ProductID already exists")

    collection.insert_one(product.dict())
    return {"message": "Product added successfully", "product": product}


@app.delete("/deleteOne")
def delete_product(product_id: str):
    result = collection.delete_one({"ProductID": product_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {"message": f"Product with ID {product_id} deleted successfully"}


@app.get("/startsWith")
def get_products_starting_with(letter: str):
    if len(letter) != 1 or not letter.isalpha():
        raise HTTPException(status_code=400, detail="Query must be a single letter.")

    regex_query = f"^{letter.upper()}"

    # Search with case-insensitive regex
    products = list(collection.find(
        {"Name": {"$regex": regex_query, "$options": "i"}},
        {"_id": 0}
    ))

    return {"products": products}

@app.get("/paginate")
def paginate_products(start_id: int, end_id: int):
    if start_id > end_id:
        raise HTTPException(status_code=400, detail="start_id must be less than or equal to end_id")

    # Query between range
    products = list(collection.find(
        {"ProductID": {"$gte": start_id, "$lte": end_id}},
        {"_id": 0}
    ).limit(10))  # Limit to 10 results

    return {"products": products}


@app.get("/convert")
def convert_to_euro(product_id: str, currency: str = Query(default="EUR")):
    product = collection.find_one({"ProductID": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        # Frankfurter API doesn't require an API key
        url = f"https://api.frankfurter.app/latest?amount=1&from=USD&to={currency}"
        response = requests.get(url)
        data = response.json()

        rate = data["rates"][currency]
    except Exception as e:
        print("Exchange rate fetch error:", e)
        raise HTTPException(status_code=500, detail="Failed to fetch exchange rate")

    usd_price = product["UnitPrice"]
    converted_price = round(usd_price * rate, 2)

    return {
        "product": product["Name"],
        "price_in_usd": usd_price,
        f"price_in_{currency.lower()}": converted_price,
        "rate_used": rate
    }



