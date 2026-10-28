from datetime import date
from decimal import Decimal
from database import get_client, get_products, get_customers
def display_customers(customers):
    print("\n========== CUSTOMERS ==========")
    print(f"{'Customer ID':<15}{'Customer Name':<25}")
    print("-" * 40)

    for customer in customers:
        print(f"{customer['customer_id']:<15}{customer['name']:<25}")


def display_products(products):
    print("\n========== PRODUCTS ==========")
    print(f"{'Product ID':<15}{'Product Name':<25}{'Price':>10}")
    print("-" * 55)

    for product in products:
        product_id = product["product_id"]
        product_name = product["product_name"]
        price = float(product["price"])

        print(f"{product_id:<15}{product_name:<25}${price:>9.2f}")

# Ask for a valid customer ID
def get_customer_id(customers):
    valid_ids = [customer["customer_id"] for customer in customers]

    while True:
        try:
            customer_id = int(input("\nEnter Customer ID: "))

            if customer_id in valid_ids:
                return customer_id

            print("Customer ID does not exist. Please try again.")

        except ValueError:
            print("Invalid input. Please enter a whole number.")


# Ask for a valid product ID
def get_product_id(products):
    valid_ids = [product["product_id"] for product in products]

    while True:
        try:
            product_id = int(input("Enter Product ID: "))

            if product_id in valid_ids:
                return product_id

            print("Product ID does not exist. Please try again.")

        except ValueError:
            print("Invalid input. Please enter a whole number.")


# Ask for a valid quantity
def get_quantity():
    while True:
        try:
            quantity = int(input("Enter Quantity: "))

            if quantity > 0:
                return quantity

            print("Quantity must be greater than zero.")

        except ValueError:
            print("Invalid quantity. Enter a positive whole number.")

# Ask the user to confirm the order
def confirm_order():
    while True:
        answer = input("\nConfirm purchase? (Y/N): ").strip().lower()

        if answer == "y":
            return True

        elif answer == "n":
            return False

        else:
            print("Invalid response. Please enter Y or N.")

# Save the confirmed order to Supabase
def save_order(customer_id, product_id, quantity, unit_price):
    order_data = {
        "customer_id": customer_id,
        "product_id": product_id,
        "quantity": quantity,
        "order_date": date.today().isoformat(),
        "unit_price": float(unit_price)
    }

    response = (
        get_client()
        .table("orders")
        .insert(order_data, returning="representation")
        .execute()
    )

    if not response.data:
        raise RuntimeError("The database did not return the inserted order.")

    return response.data[0]["order_id"]

# Retrieve the saved order from Supabase
def verify_order(order_id):
    response = (
        get_client()
        .table("orders")
        .select("*")
        .eq("order_id", order_id)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]

# Display the saved order
def display_verified_order(order, customer_name, product_name):
    quantity = order["quantity"]
    unit_price = Decimal(str(order["unit_price"]))
    total = quantity * unit_price

    print("\n========== VERIFIED ORDER ==========")

    print(
        f"{'Order ID':<10}"
        f"{'Customer':<20}"
        f"{'Product':<20}"
        f"{'Quantity':<10}"
        f"{'Unit Price':<15}"
        f"{'Total':<15}"
        f"{'Order Date':<15}"
    )

    print("-" * 105)

    print(
        f"{order['order_id']:<10}"
        f"{customer_name:<20}"
        f"{product_name:<20}"
        f"{quantity:<10}"
        f"${unit_price:<14.2f}"
        f"${total:<14.2f}"
        f"{order['order_date']:<15}"
    )

def main():
    try:
        customers = get_customers()
        products = get_products()

        display_customers(customers)
        display_products(products)

        # Collect validated input
        customer_id = get_customer_id(customers)
        product_id = get_product_id(products)
        quantity = get_quantity()

        # Find the selected customer and product
        customer = next(
            c for c in customers
            if c["customer_id"] == customer_id
        )

        product = next(
            p for p in products
            if p["product_id"] == product_id
        )

        customer_name = customer["name"]
        product_name = product["product_name"]

        unit_price = Decimal(str(product["price"]))
        total = unit_price * quantity

        # Display order summary
        print("\n========== ORDER SUMMARY ==========")
        print("Customer:", customer_name)
        print("Product:", product_name)
        print("Quantity:", quantity)
        print(f"Unit Price: ${unit_price:.2f}")
        print(f"Order Total: ${total:.2f}")

        # Confirm or cancel the order
        if not confirm_order():
            print("\nOrder cancelled. No record was inserted.")
            return

        # Save the order
        try:
            order_id = save_order(
                customer_id,
                product_id,
                quantity,
                unit_price
            )

            print("\nOrder successfully saved!")

        except Exception:
            print("Order could not be saved. Check your database permissions or connection.")
            return

        # Verify the order with a new query
        try:
            saved_order = verify_order(order_id)

            if saved_order:
                display_verified_order(
                    saved_order,
                    customer_name,
                    product_name
                )
            else:
                print("Order saved, but verification could not be completed.")

        except Exception:
            print("Order saved, but verification could not be completed.")

    except Exception as e:
        print("An error occurred:", type(e).__name__, str(e))


if __name__ == "__main__":
    main()