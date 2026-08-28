import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "sales.db")

def setup_database():
    print(f"Creating database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Create orders table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id TEXT PRIMARY KEY,
        customer_name TEXT NOT NULL,
        status TEXT NOT NULL,
        total_amount REAL NOT NULL
    )
    """)

    # 2. Create order_items table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT NOT NULL,
        product_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders (order_id)
    )
    """)

    # 3. Create inventory table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        product_name TEXT PRIMARY KEY,
        stock_count INTEGER NOT NULL
    )
    """)

    # Clear existing data to ensure fresh insert
    cursor.execute("DELETE FROM order_items")
    cursor.execute("DELETE FROM orders")
    cursor.execute("DELETE FROM inventory")

    # Insert sample orders
    orders_data = [
        ("OD-101", "Nguyen Van A", "Delivered", 150.00),
        ("OD-102", "Tran Thi B", "Shipping", 85.50),
        ("OD-103", "Luu Quang C", "Pending", 420.00)
    ]
    cursor.executemany("INSERT INTO orders VALUES (?, ?, ?, ?)", orders_data)

    # Insert sample order items
    items_data = [
        ("OD-101", "Laptop", 1, 120.00),
        ("OD-101", "Mouse", 1, 30.00),
        ("OD-102", "Keyboard", 1, 85.50),
        ("OD-103", "Monitor", 2, 200.00),
        ("OD-103", "Cable", 2, 10.00)
    ]
    cursor.executemany("INSERT INTO order_items (order_id, product_name, quantity, price) VALUES (?, ?, ?, ?)", items_data)

    # Insert sample inventory
    inventory_data = [
        ("Laptop", 15),
        ("Mouse", 120),
        ("Keyboard", 45),
        ("Monitor", 8),
        ("Cable", 300)
    ]
    cursor.executemany("INSERT INTO inventory VALUES (?, ?)", inventory_data)

    conn.commit()
    conn.close()
    print("✅ Database sales.db initialized successfully with sample data.")

if __name__ == "__main__":
    setup_database()
