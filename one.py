from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


COLUMNS = ["Order_ID", "Product", "Category", "Quantity", "Price"]


def load_orders(csv_name):
    # Find a relative CSV path next to this Python file.
    csv_path = Path(csv_name)
    if not csv_path.is_absolute():
        csv_path = Path(__file__).resolve().parent / csv_path

    try:
        data = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    except FileNotFoundError:
        print(f"Error: file '{csv_path.name}' was not found.")
        return None
    except Exception as error:
        print(f"Could not read the CSV file: {error}")
        return None

    missing = [column for column in COLUMNS if column not in data.columns]
    if missing:
        print("Missing CSV column(s): " + ", ".join(missing))
        print("Required columns: " + ", ".join(COLUMNS))
        return None

    valid_rows = []

    for index, row in data.iterrows():
        # Number data rows from 1, matching the assignment's test cases.
        row_number = index + 1

        order_id = row["Order_ID"].strip()
        product = row["Product"].strip()
        category = row["Category"].strip()
        quantity_text = row["Quantity"].strip()
        price_text = row["Price"].strip()

        try:
            quantity = int(quantity_text)
        except ValueError:
            print(f"Row {row_number} skipped: invalid Quantity '{quantity_text}'")
            continue

        try:
            price = float(price_text)
        except ValueError:
            print(f"Row {row_number} skipped: invalid Price '{price_text}'")
            continue

        if quantity <= 0:
            print(f"Row {row_number} skipped: Quantity must be positive")
            continue

        if price <= 0:
            print(f"Row {row_number} skipped: Price must be positive")
            continue

        if not order_id or not product or not category:
            print(f"Row {row_number} skipped: required information is missing")
            continue

        valid_rows.append({
            "Order_ID": order_id,
            "Product": product,
            "Category": category,
            "Quantity": quantity,
            "Price": price,
        })

    orders = pd.DataFrame(valid_rows, columns=COLUMNS)

    if not orders.empty:
        duplicate_rows = orders.duplicated(subset="Order_ID", keep="first")
        for _, duplicate in orders[duplicate_rows].iterrows():
            print(f"Duplicate order skipped: Order_ID '{duplicate['Order_ID']}'")
        orders = orders[~duplicate_rows].copy()

    orders["Revenue"] = orders["Quantity"] * orders["Price"]
    return orders


def show_summary(orders):
    print("\n--- Sales Summary ---")
    print(f"Total Revenue: {orders['Revenue'].sum():g}")
    print(f"Orders: {len(orders)}")
    print(f"Units sold: {orders['Quantity'].sum()}")

    product_revenue = (
        orders.groupby("Product")["Revenue"]
        .sum()
        .sort_values(ascending=False)
    )

    if product_revenue.empty:
        print("Top product: None")
        print("No products to display.")
        return

    print(f"Top product: {product_revenue.index[0]} "
          f"({product_revenue.iloc[0]:g})")

    print("\nTop 5 products by revenue:")
    for product, revenue in product_revenue.head(5).items():
        print(f"{product}: {revenue:g}")


def show_category_revenue(orders):
    category_revenue = (
        orders.groupby("Category")["Revenue"]
        .sum()
        .sort_values(ascending=False)
    )

    total_revenue = category_revenue.sum()

    if category_revenue.empty or total_revenue == 0:
        print("No category revenue to display.")
        return

    print("\n--- Category-wise Revenue ---")
    for category, revenue in category_revenue.items():
        percentage = revenue / total_revenue * 100
        print(f"{category}: {revenue:g} ({percentage:.2f}%)")

    category_revenue.plot.pie(
        autopct="%1.2f%%",
        startangle=90,
        ylabel=""
    )
    plt.title("Category-wise Revenue")
    plt.tight_layout()
    plt.show()


def show_top_products_chart(orders):
    product_revenue = (
        orders.groupby("Product")["Revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
    )

    if product_revenue.empty:
        print("No product revenue to display.")
        return

    product_revenue.plot(kind="bar", color="steelblue")
    plt.title("Top 5 Products by Revenue")
    plt.xlabel("Product")
    plt.ylabel("Revenue")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.show()


def main():
    print("E-Commerce Sales Analyzer")
    orders = load_orders("orders.csv")

    if orders is None:
        return

    while True:
        print("\n1. Summary")
        print("2. Category-wise revenue and pie chart")
        print("3. Top 5 products bar chart")
        print("4. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            show_summary(orders)
        elif choice == "2":
            show_category_revenue(orders)
        elif choice == "3":
            show_top_products_chart(orders)
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()