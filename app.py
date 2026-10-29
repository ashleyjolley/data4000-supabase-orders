import hmac
import logging
import os
from decimal import Decimal
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from streamlit.errors import StreamlitSecretNotFoundError

from config import get_settings
from database import (
    PriceChangedError,
    create_order,
    get_client,
    get_customers,
    get_order_by_id,
    get_orders,
    get_product,
    get_products,
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv(Path(__file__).with_name(".env"))


def _read_secrets():
    try:
        return dict(st.secrets)
    except StreamlitSecretNotFoundError:
        return {}


def _relation_value(order, relation, field):
    related = order.get(relation) or {}
    if isinstance(related, list):
        related = related[0] if related else {}
    return related.get(field, "")


def _order_row(order):
    unit_price = Decimal(str(order["unit_price"]))
    quantity = int(order["quantity"])
    return {
        "Order ID": order["order_id"],
        "Customer": _relation_value(order, "customers", "name"),
        "Product": _relation_value(order, "products", "product_name"),
        "Quantity": quantity,
        "Unit Price": float(unit_price),
        "Total": float(unit_price * quantity),
        "Order Date": order["order_date"],
    }


def _display_order_table(order, key):
    st.dataframe(
        [_order_row(order)],
        hide_index=True,
        use_container_width=True,
        column_config={
            "Unit Price": st.column_config.NumberColumn(format="$%.2f"),
            "Total": st.column_config.NumberColumn(format="$%.2f"),
        },
        key=key,
    )


st.set_page_config(page_title="Campus Store Order Entry", page_icon="🛒")
st.title("Campus Store Order Entry")
st.write(
    "Choose a customer and product, review the current price, and confirm "
    "to save one fictional classroom order to Supabase."
)

secrets = _read_secrets()
app_password = str(secrets.get("APP_PASSWORD") or os.getenv("APP_PASSWORD", "")).strip()
if not app_password:
    st.error(
        "The app is not configured for protected access. Set APP_PASSWORD in "
        "Streamlit Community Cloud secrets or your local .env file."
    )
    st.stop()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    with st.form("access_gate"):
        entered_password = st.text_input("Classroom app password", type="password")
        login_submitted = st.form_submit_button("Continue")
    if login_submitted:
        if hmac.compare_digest(entered_password, app_password):
            st.session_state.authenticated = True
        else:
            st.error("That password is not correct.")
    if not st.session_state.authenticated:
        st.stop()

supabase_settings = secrets.get("supabase", {})
try:
    supabase_url, supabase_key = get_settings(
        secrets.get("SUPABASE_URL") or supabase_settings.get("url"),
        secrets.get("SUPABASE_SECRET_KEY") or supabase_settings.get("secret_key"),
    )
    client = get_client(supabase_url, supabase_key)
    customers = get_customers(client=client)
    products = get_products(client=client)
    orders = get_orders(client=client)
except Exception:
    logger.exception("Could not load the Supabase data for the order-entry app.")
    st.error(
        "Could not connect to Supabase or load the classroom data. Check the "
        "app's Supabase URL, secret key, project status, and database access."
    )
    st.stop()

if st.button("Refresh Data"):
    st.success("Customer, product, and order data refreshed from Supabase.")

st.subheader("Customers")
customer_rows = [
    {"Customer ID": customer["customer_id"], "Name": customer["name"]}
    for customer in customers
]
st.dataframe(customer_rows, hide_index=True, use_container_width=True)

st.subheader("Products")
product_rows = [
    {
        "Product ID": product["product_id"],
        "Product Name": product["product_name"],
        "Category": product["category"],
        "Price": float(product["price"]),
    }
    for product in products
]
st.dataframe(
    product_rows,
    hide_index=True,
    use_container_width=True,
    column_config={"Price": st.column_config.NumberColumn(format="$%.2f")},
)

st.subheader("Enter an order")
if not customers or not products:
    st.info("Add customers and products to Supabase before entering an order.")
    st.stop()

customer_by_id = {int(customer["customer_id"]): customer for customer in customers}
product_by_id = {int(product["product_id"]): product for product in products}
customer_id = st.selectbox(
    "Customer",
    list(customer_by_id),
    format_func=lambda value: (
        f"{customer_by_id[value]['name']} (ID {value})"
    ),
)
product_id = st.selectbox(
    "Product",
    list(product_by_id),
    format_func=lambda value: (
        f"{product_by_id[value]['product_name']} (ID {value})"
    ),
)
quantity = st.number_input(
    "Quantity",
    min_value=1,
    max_value=100000,
    value=1,
    step=1,
    format="%d",
)

selection = (customer_id, product_id, int(quantity))
if "order_review" not in st.session_state:
    st.session_state.order_review = None
if "review_version" not in st.session_state:
    st.session_state.review_version = 0

review = st.session_state.order_review
if review is not None and review["selection"] != selection:
    st.session_state.order_review = None
    st.session_state.review_version += 1
    review = None
    st.info("Your selection changed. Review the order again before confirming.")

if st.button("Review order"):
    try:
        current_product = get_product(product_id, client=client)
        st.session_state.review_version += 1
        st.session_state.order_review = {
            "selection": selection,
            "unit_price": Decimal(str(current_product["price"])),
        }
        review = st.session_state.order_review
    except Exception:
        logger.exception("Could not retrieve the current product price.")
        st.error("Could not check the current price. Please try again.")
        review = None

if review is not None:
    unit_price = review["unit_price"]
    st.markdown("#### Review your order")
    st.write(f"**Customer:** {customer_by_id[customer_id]['name']}")
    st.write(f"**Product:** {product_by_id[product_id]['product_name']}")
    st.write(f"**Quantity:** {quantity}")
    st.write(f"**Unit price:** ${unit_price:,.2f}")
    st.write(f"**Total:** ${unit_price * int(quantity):,.2f}")

    confirm_key = f"confirm_order_{st.session_state.review_version}"
    confirmed = st.checkbox(
        "I have reviewed these details and confirm this order.",
        key=confirm_key,
    )
    submitted = st.button("Submit order", type="primary")
    if submitted and not confirmed:
        st.warning("Check the confirmation box before submitting.")
    elif submitted:
        try:
            latest_product = get_product(product_id, client=client)
            latest_price = Decimal(str(latest_product["price"]))
            if latest_price != unit_price:
                st.session_state.order_review["unit_price"] = latest_price
                st.session_state.review_version += 1
                st.warning(
                    f"The price changed to ${latest_price:,.2f}. Review and "
                    "confirm the updated total before submitting."
                )
                st.rerun()

            order = create_order(
                customer_id,
                product_id,
                int(quantity),
                expected_unit_price=unit_price,
                client=client,
            )
        except PriceChangedError as error:
            st.session_state.order_review["unit_price"] = error.current_price
            st.session_state.review_version += 1
            st.warning(
                f"The price changed to ${error.current_price:,.2f}. Review and "
                "confirm the updated total before submitting."
            )
            st.rerun()
        except Exception:
            logger.exception("Could not save the confirmed order.")
            st.error(
                "The order could not be saved. Check the customer and product "
                "still exist, then try again."
            )
        else:
            order_id = order["order_id"]
            st.session_state.last_saved_order_id = order_id
            st.session_state.last_verified_order = None
            st.session_state.last_verification_failed = False
            st.session_state.order_review = None
            st.success(f"Order {order_id} was saved.")
            try:
                orders = get_orders(client=client)
            except Exception:
                logger.exception("Could not refresh order history after saving order %s.", order_id)
                st.session_state.order_history_refresh_failed = True
            else:
                st.session_state.order_history_refresh_failed = False
            try:
                st.session_state.last_verified_order = get_order_by_id(
                    order_id, client=client
                )
            except Exception:
                logger.exception(
                    "Order %s was saved but could not be retrieved for verification.",
                    order_id,
                )
                st.session_state.last_verification_failed = True

if "last_saved_order_id" in st.session_state:
    st.subheader("Saved order verification")
    verified_order = st.session_state.last_verified_order
    if verified_order is not None:
        _display_order_table(verified_order, "verified_order")
    elif st.session_state.last_verification_failed:
        order_id = st.session_state.last_saved_order_id
        st.warning(
            f"Order {order_id} was saved, but could not be retrieved for "
            "verification. It was not submitted again."
        )
        if st.button("Retry verification"):
            try:
                st.session_state.last_verified_order = get_order_by_id(
                    order_id, client=client
                )
                st.session_state.last_verification_failed = False
            except Exception:
                logger.exception("Could not verify saved order %s.", order_id)
                st.error("Verification is still unavailable. The saved order was not resubmitted.")
            else:
                st.rerun()

st.subheader("Order History")
if st.session_state.get("order_history_refresh_failed"):
    st.warning(
        "The order was saved, but order history could not be refreshed. "
        "Use Refresh Data to try again."
    )
if orders:
    history_customers = {None: "All customers"}
    history_customers.update({
        int(customer["customer_id"]): customer["name"]
        for customer in customers
    })
    history_customer_id = st.selectbox(
        "Filter history by customer",
        list(history_customers),
        format_func=lambda value: history_customers[value],
    )
    if history_customer_id is not None:
        orders = [
            order for order in orders
            if int(order["customer_id"]) == history_customer_id
        ]
    history_rows = [_order_row(order) for order in orders]
    st.dataframe(
        history_rows,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Unit Price": st.column_config.NumberColumn(format="$%.2f"),
            "Total": st.column_config.NumberColumn(format="$%.2f"),
        },
    )
    total_value = sum(
        Decimal(str(order["unit_price"])) * int(order["quantity"])
        for order in orders
    )
    st.metric("Filtered order value", f"${total_value:,.2f}")
else:
    st.info("No orders have been recorded yet.")
