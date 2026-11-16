import streamlit as st
from openpyxl import load_workbook

st.title("Canteen Sales Tracker")

# R1 - Upload

uploaded_file = st.file_uploader(
    "Upload your Excel file",
    type=["xlsx"]
)

if uploaded_file is None:
    st.info("Please upload an Excel file to continue.")
    st.stop()


# R2 - Read Excel into dictionaries

workbook = load_workbook(uploaded_file, data_only=True)

sheet = workbook.active

rows = sheet.iter_rows(values_only=True)

headers = next(rows)

orders = []

for row in rows:

    if all(value is None for value in row):
        continue

    order = dict(zip(headers, row))

    orders.append(order)


# R3 - Calculate totals and skip bad rows

bad_rows = 0

valid_orders = []

for order in orders:

    price = order["Price"]
    quantity = order["Quantity"]

    if isinstance(price, (int, float)) and isinstance(quantity, (int, float)):

        order["Total"] = price * quantity

        valid_orders.append(order)

    else:

        bad_rows += 1

orders = valid_orders

if bad_rows > 0:
    st.warning(f"{bad_rows} invalid order(s) were skipped.")


# R4 - Filters

campuses = ["All campuses"]

for order in orders:

    if order["Campus"] not in campuses:
        campuses.append(order["Campus"])


categories = ["All categories"]

for order in orders:

    if order["Category"] not in categories:
        categories.append(order["Category"])


selected_campus = st.sidebar.selectbox(
    "Select Campus",
    campuses
)

selected_category = st.sidebar.selectbox(
    "Select Category",
    categories
)


shown = []

for order in orders:

    campus_match = (
        selected_campus == "All campuses"
        or order["Campus"] == selected_campus
    )

    category_match = (
        selected_category == "All categories"
        or order["Category"] == selected_category
    )

    if campus_match and category_match:
        shown.append(order)


# R5 - Summary metrics

total_sales = 0

for order in shown:
    total_sales += order["Total"]

number_of_orders = len(shown)

if number_of_orders > 0:
    average_order = total_sales / number_of_orders
else:
    average_order = 0


col1, col2, col3 = st.columns(3)

col1.metric("Total Sales", f"J${total_sales:,}")

col2.metric("Number of Orders", number_of_orders)

col3.metric("Average Order", f"J${average_order:,.0f}")


# R6 - Best-selling item

item_quantities = {}

for order in shown:

    item = order["Item"]

    quantity = order["Quantity"]

    if item in item_quantities:

        item_quantities[item] += quantity

    else:

        item_quantities[item] = quantity


st.subheader("Best-Selling Item")

if item_quantities:

    best_seller = max(
        item_quantities,
        key=item_quantities.get
    )

    st.success(
        f"{best_seller} - {item_quantities[best_seller]} sold"
    )

else:

    st.info("No orders available.")


# R7 - Order table

st.subheader("Order Details")

st.dataframe(shown)


# R8 - Histogram

histogram = {}

for order in shown:

    total = order["Total"]

    range_start = (total // 500) * 500

    if range_start in histogram:

        histogram[range_start] += 1

    else:

        histogram[range_start] = 1


st.subheader("Order Total Distribution")

if histogram:

    chart_data = {
        "Range": sorted(histogram.keys()),
        "Orders": [
            histogram[value]
            for value in sorted(histogram.keys())
        ]
    }

    st.bar_chart(
        chart_data,
        x="Range",
        y="Orders"
    )


# R9 - Sales by item

item_sales = {}

for order in shown:

    item = order["Item"]

    total = order["Total"]

    if item in item_sales:

        item_sales[item] += total

    else:

        item_sales[item] = total


st.subheader("Sales by Item")

if item_sales:

    chart_data = {
        "Item": list(item_sales.keys()),
        "Sales": list(item_sales.values())
    }

    st.bar_chart(
        chart_data,
        x="Item",
        y="Sales"
    )