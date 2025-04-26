from db import get_connection
from datetime import datetime
def add_product(name, category, price, quantity):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, stock_quantity FROM Product
        WHERE name = ? AND category = ? AND price_per_unit = ?
    """, (name, category, price))
    existing = cur.fetchone()

    if existing:
        product_id, current_qty = existing
        new_qty = current_qty + quantity
        cur.execute("UPDATE Product SET stock_quantity = ? WHERE id = ?", (new_qty, product_id))
    else:
        cur.execute(
            "INSERT INTO Product (name, category, price_per_unit, stock_quantity) VALUES (?, ?, ?, ?)",
            (name, category, price, quantity)
        )

    conn.commit()
    conn.close()

def get_products_grouped_by_category():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT category, id, name, price_per_unit, stock_quantity FROM Product ORDER BY category, name')
    rows = cur.fetchall()
    conn.close()

    grouped = {}
    for cat, pid, name, price, qty in rows:
        grouped.setdefault(cat, []).append((pid, name, price, qty))
    return grouped

def sell_multiple_products(purchases):
    conn = get_connection()
    cur = conn.cursor()
    errors = []
    total = 0.0

    try:
        sale_date = datetime.now().date()
        cur.execute("INSERT INTO Receipt (sale_date) VALUES (?)", (sale_date,))
        receipt_id = cur.lastrowid

        for pid, qty in purchases:
            cur.execute("SELECT stock_quantity, price_per_unit FROM Product WHERE id=?", (pid,))
            result = cur.fetchone()
            if not result:
                errors.append(f"Товар с ID {pid} не найден.")
                continue

            available, price = result
            if qty > available:
                errors.append(f"Недостаточно товара (ID {pid}): доступно {available}, запрошено {qty}")
                continue

            cur.execute("UPDATE Product SET stock_quantity = stock_quantity - ? WHERE id=?", (qty, pid))

            total_price = qty * price
            cur.execute('''INSERT INTO ReceiptItem (receipt_id, product_id, quantity, total_price)
                           VALUES (?, ?, ?, ?)''', (receipt_id, pid, qty, total_price))

            total += total_price

        cur.execute("DELETE FROM Product WHERE stock_quantity <= 0")

        conn.commit()

    except Exception as e:
        conn.rollback()
        return False, [str(e)]
    finally:
        conn.close()

    return (True, total) if not errors else (False, errors)

def get_sales_report(date):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT p.name, SUM(ri.quantity), SUM(ri.total_price)
        FROM ReceiptItem ri
        JOIN Receipt r ON ri.receipt_id = r.id
        JOIN Product p ON ri.product_id = p.id
        WHERE r.sale_date = ?
        GROUP BY p.name
    ''', (date,))
    rows = cur.fetchall()

    cur.execute('''
        SELECT SUM(total_price)
        FROM ReceiptItem
        JOIN Receipt r ON ReceiptItem.receipt_id = r.id
        WHERE r.sale_date = ?
    ''', (date,))
    total = cur.fetchone()[0] or 0

    conn.close()
    return rows, total
