import pandas as pd
from pymongo import MongoClient

df = pd.read_csv("auto_products.csv")

df.rename(columns={
    "Product ID": "ProductID",
    "Unit Price": "UnitPrice",
    "Stock Quantity": "StockQuantity"
}, inplace=True)

records = df.to_dict(orient='records')

client = MongoClient("mongodb://mongo:27017/")
db = client["inventory_db"]
collection = db["products"]

collection.delete_many({})  # Reset
collection.insert_many(records)