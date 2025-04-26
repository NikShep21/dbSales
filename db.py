import sqlite3

DB_FILE = 'store.db'

def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS Product (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        price_per_unit REAL NOT NULL,
        stock_quantity INTEGER NOT NULL
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS Receipt (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_date TEXT NOT NULL
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS ReceiptItem (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        receipt_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        total_price REAL NOT NULL,
        FOREIGN KEY (receipt_id) REFERENCES Receipt(id),
        FOREIGN KEY (product_id) REFERENCES Product(id)
    )''')

    conn.commit()
    conn.close()
