import tkinter as tk
from tkinter import ttk, messagebox
from db import init_db
from models import (
    add_product,
    sell_multiple_products,
    get_sales_report,
    get_receipts_by_date,
    get_products_grouped_by_category,
)

def create_centered_window(title, size="600x400"):
    win = tk.Toplevel()
    win.title(title)
    win.geometry(size)
    win.config(padx=20, pady=20)
    frame = tk.Frame(win)
    frame.pack(anchor="center")
    return win, frame

def add_window():
    win, frame = create_centered_window("Добавить товар")
    fields = ["Название", "Категория", "Цена", "Количество"]
    entries = {}

    for i, label in enumerate(fields):
        tk.Label(frame, text=label, font=("Arial", 12)).grid(row=i, column=0, pady=5, sticky="e")
        ent = tk.Entry(frame, font=("Arial", 12))
        ent.grid(row=i, column=1, pady=5, padx=10)
        entries[label] = ent

    def save():
        try:
            name = entries["Название"].get()
            cat = entries["Категория"].get()
            price = float(entries["Цена"].get())
            qty = int(entries["Количество"].get())
            add_product(name, cat, price, qty)
            messagebox.showinfo("Успех", "Товар добавлен")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    ttk.Button(frame, text="Сохранить", command=save, width=20, padding=10).grid(row=4, columnspan=2, pady=10)
def receipt_window():
    win, frame = create_centered_window("Чеки по дате")

    # Ввод даты
    tk.Label(frame, text="Введите дату (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=10, pady=10)
    date_entry = ttk.Entry(frame, width=20)
    date_entry.grid(row=0, column=1, padx=10, pady=10)

    def show_receipts():
        # Получаем дату из поля ввода
        date = date_entry.get()
        if not date:
            tk.messagebox.showerror("Ошибка", "Пожалуйста, введите дату.")
            return

        # Получаем чеки по введенной дате
        receipts_data = get_receipts_by_date(date)
        if not receipts_data:
            tk.messagebox.showinfo("Информация", "Чеки на эту дату не найдены.")
            return

        # Очищаем предыдущий вывод (если он был)
        for widget in frame.winfo_children():
            widget.grid_forget()

        row = 1
        for receipt_id, sale_date, items in receipts_data:
            tk.Label(frame, text=f"Чек #{receipt_id} ({sale_date})", font=("Arial", 12, "bold")).grid(row=row, column=0, sticky="w", pady=(10, 0))
            row += 1
            total_sum = 0
            for name, qty, total_price in items:
                tk.Label(frame, text=f"{name}: {qty} шт, {total_price:.2f} руб").grid(row=row, column=0, sticky="w", pady=2)
                total_sum += total_price
                row += 1
            tk.Label(frame, text=f"Итого: {total_sum:.2f} руб", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky="w", pady=10)
            row += 1

        ttk.Button(frame, text="Закрыть", command=win.destroy, width=20, padding=10).grid(row=row, column=0, columnspan=2, pady=10)

    ttk.Button(frame, text="Показать чеки", command=show_receipts, width=20, padding=10).grid(row=1, column=0, columnspan=2, pady=10)

def sale_window():
    win, frame = create_centered_window("Продажа")
    win.geometry("450x700")
    win.config(padx=20, pady=20)
    grouped = get_products_grouped_by_category()
    vars_map = {}
    row = 0

    for cat, items in grouped.items():
        tk.Label(frame, text=f"[{cat}]", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky="w", pady=(10, 0))
        row += 1
        for pid, name, price, qty in items:
            tk.Label(frame, text=f"{name} ({qty} шт, {price} руб)").grid(row=row, column=0, sticky="w", pady=2)
            var = tk.IntVar()
            tk.Entry(frame, textvariable=var, width=5).grid(row=row, column=1, padx=5)
            vars_map[pid] = var
            row += 1

    def process():
        purchases = [(pid, var.get()) for pid, var in vars_map.items() if var.get() > 0]
        if not purchases:
            return messagebox.showwarning("Нет выбора", "Выберите хотя бы один товар.")
        success, result = sell_multiple_products(purchases)
        if success:
            messagebox.showinfo("Успешно", f"Общая сумма продажи: {result:.2f} руб")
            win.destroy()
        else:
            messagebox.showerror("Ошибка", "\n".join(result))

    ttk.Button(frame, text="Продать", command=process, width=20, padding=10).grid(row=row, column=0, columnspan=2, pady=10)

def report_window():
    win, frame = create_centered_window("Отчет по дате")

    tk.Label(frame, text="Введите дату (YYYY-MM-DD):").grid(row=0, column=0, pady=5, sticky="e")
    date_entry = tk.Entry(frame)
    date_entry.grid(row=0, column=1, pady=5, padx=10)

    text = tk.Text(frame, width=50, height=15)
    text.grid(row=2, column=0, columnspan=2, pady=10)

    def generate():
        date = date_entry.get()
        if not date:
            return messagebox.showwarning("Ошибка", "Пожалуйста, введите дату.")
        report, total = get_sales_report(date)
        text.delete(1.0, tk.END)
        for name, qty, sum_ in report:
            text.insert(tk.END, f"{name}: {qty} шт, {sum_:.2f} руб\n")
        text.insert(tk.END, f"\nОбщая выручка: {total:.2f} руб")

    ttk.Button(frame, text="Показать", command=generate, width=20, padding=10).grid(row=1, column=0, columnspan=2, pady=5)



init_db()
root = tk.Tk()
root.title("Учет товаров")
root.geometry("400x400")
root.config(padx=20, pady=20)

for text, cmd in [
    ("Добавить товар", add_window),
    ("Продажа", sale_window),
    ("Отчет по дате", report_window),
    ("Чеки", receipt_window)
    
]:
    ttk.Button(root, text=text, command=cmd, width=20, padding=10).pack(fill='x', pady=10)

root.mainloop()
