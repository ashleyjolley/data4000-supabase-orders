"""Reusable API functions for local classroom scripts and a future backend.
Every .execute() sends an HTTP request; this is not a direct PostgreSQL connection.
"""
from datetime import date
from decimal import Decimal
from functools import lru_cache
from supabase import create_client
from config import get_settings


@lru_cache(maxsize=1)
def get_client(url=None, key=None):
    if (url is None) != (key is None):
        raise ValueError("Both Supabase URL and secret key must be provided together.")
    if url is None:
        url, key = get_settings()
    else:
        url, key = get_settings(url, key)
    return create_client(url, key)


def get_products(max_price=None, client=None):
    query = (client or get_client()).table("products").select("*")
    if max_price is not None:
        query = query.lte("price", float(max_price))
    return query.order("product_id").execute().data


def get_customers(city=None, client=None):
    query = (client or get_client()).table("customers").select("*")
    if city:
        query = query.eq("city", city)
    return query.order("customer_id").execute().data


def get_product(product_id, client=None):
    products = ((client or get_client()).table("products").select("product_id, price")
                .eq("product_id", int(product_id)).execute().data)
    if not products:
        raise ValueError("Product not found.")
    return products[0]


def add_customer(name, email, city):
    if not all(value.strip() for value in (name, email, city)):
        raise ValueError("Name, email, and city are required.")
    response = get_client().table("customers").insert({
        "name": name.strip(), "email": email.strip().lower(), "city": city.strip()
    }).execute()
    return response.data[0]


def update_product_price(product_id, price):
    price = Decimal(str(price))
    if not price.is_finite() or price < 0 or price != price.quantize(Decimal("0.01")):
        raise ValueError("Use a nonnegative price with at most two decimal places.")
    response = (get_client().table("products").update({"price": str(price)})
                .eq("product_id", int(product_id)).execute())
    if not response.data:
        raise ValueError("Product not found.")
    return response.data[0]


class PriceChangedError(ValueError):
    def __init__(self, current_price):
        super().__init__("The product price changed. Review and confirm the updated price.")
        self.current_price = Decimal(str(current_price))


def create_order(
    customer_id, product_id, quantity, expected_unit_price=None, client=None
):
    if type(quantity) is not int or quantity <= 0:
        raise ValueError("Quantity must be a positive integer.")
    db = client or get_client()
    customers = (db.table("customers").select("customer_id")
                 .eq("customer_id", int(customer_id)).execute().data)
    if not customers:
        raise ValueError("Customer not found.")
    # Snapshot the current price so later catalog changes do not rewrite past revenue.
    products = (db.table("products").select("product_id, price")
                .eq("product_id", int(product_id)).execute().data)
    if not products:
        raise ValueError("Product not found.")
    unit_price = Decimal(str(products[0]["price"]))
    if (expected_unit_price is not None
            and unit_price != Decimal(str(expected_unit_price))):
        raise PriceChangedError(unit_price)
    response = db.table("orders").insert({
        "customer_id": int(customer_id), "product_id": int(product_id),
        "quantity": quantity, "order_date": date.today().isoformat(),
        "unit_price": str(unit_price)
    }, returning="representation").execute()
    if not response.data:
        raise RuntimeError("The database did not return the inserted order.")
    return response.data[0]


def get_orders(client=None):
    # Foreign keys let the API embed the related records in one response.
    return ((client or get_client()).table("orders")
            .select("*, customers(name, city), products(product_name)")
            .order("order_id", desc=True).execute().data)


def get_order_by_id(order_id, client=None):
    orders = ((client or get_client()).table("orders")
              .select("*, customers(name), products(product_name)")
              .eq("order_id", int(order_id)).execute().data)
    if not orders:
        raise ValueError("The saved order could not be found.")
    return orders[0]


def delete_order(order_id):
    return (get_client().table("orders").delete()
            .eq("order_id", int(order_id)).execute().data)
