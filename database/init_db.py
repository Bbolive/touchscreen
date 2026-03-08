import sqlite3

conn = sqlite3.connect("food.db")
c = conn.cursor()

# menus
c.execute("""
CREATE TABLE IF NOT EXISTS menus (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price INTEGER NOT NULL
)
""")

# ingredients
c.execute("""
CREATE TABLE IF NOT EXISTS ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    label TEXT NOT NULL,
    price INTEGER
)
""")

# menu ingredients
c.execute("""
CREATE TABLE IF NOT EXISTS menu_ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    menu_id INTEGER,
    ingredient_id INTEGER
)
""")

# orders
c.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_price INTEGER
)
""")

# order items
c.execute("""
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    menu_id INTEGER
)
""")

# detections
c.execute("""
CREATE TABLE IF NOT EXISTS detections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time DATETIME,
    end_time DATETIME,
    duration REAL,
    detected_menu TEXT,
    confidence REAL,
    price INTEGER,
    weight REAL
)
""")

conn.commit()
conn.close()

print("Database created successfully")