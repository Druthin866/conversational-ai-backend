import pandas as pd
from app.database import SessionLocal
from app import models
from datetime import datetime

session = SessionLocal()

def parse_date(date_str):
    try:
        return datetime.fromisoformat(date_str)
    except:
        return None

def load_csv(file_path, model, date_columns=None):
    df = pd.read_csv(file_path)
    if date_columns:
        for col in date_columns:
            df[col] = df[col].apply(parse_date)
    records = df.to_dict(orient="records")
    for record in records:
        session.add(model(**record))
    session.commit()

load_csv("users.csv", models.User, ["created_at"])
load_csv("orders.csv", models.Order, ["created_at", "returned_at", "shipped_at", "delivered_at"])
load_csv("order_items.csv", models.OrderItem, ["created_at", "shipped_at", "delivered_at", "returned_at"])
load_csv("products.csv", models.Product)
load_csv("inventory_items.csv", models.InventoryItem, ["created_at", "sold_at"])
load_csv("distribution_centers.csv", models.DistributionCenter)

print("✅ Data loaded successfully!")
