import sqlite3
import os
import tkinter as tk
from tkinter import messagebox

# Define the path for the database file on the desktop
desktop_path = os.path.expanduser("~/Desktop")
db_path = os.path.join(desktop_path, "inventory.db")

def initialize_database():
    conn = sqlite3.connect(db_path)  # Use the absolute path to the database
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        brand TEXT NOT NULL,
        price REAL NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 0
    )''')
    conn.commit()
    conn.close()

# Database operations
def add_product_with_id(product_id, name, category, brand, price, quantity):
    conn = sqlite3.connect(db_path)  # Use the absolute path to the database
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO products (id, name, category, brand, price, quantity) VALUES (?, ?, ?, ?, ?, ?)",
                       (product_id, name, category, brand, price, quantity))
        conn.commit()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Product ID already exists")
    conn.close()

def update_quantity(product_id, amount):
    conn = sqlite3.connect(db_path)  # Use the absolute path to the database
    cursor = conn.cursor()
    cursor.execute("SELECT quantity FROM products WHERE id = ?", (product_id,))
    result = cursor.fetchone()
    if result:
        new_quantity = result[0] + amount
        if new_quantity < 0:
            messagebox.showerror("Error", "Insufficient stock")
        else:
            cursor.execute("UPDATE products SET quantity = ? WHERE id = ?", (new_quantity, product_id))
            conn.commit()
    else:
        messagebox.showerror("Error", "Product not found")
    conn.close()

def check_stock(product_id):
    conn = sqlite3.connect(db_path)  # Use the absolute path to the database
    cursor = conn.cursor()
    cursor.execute("SELECT name, quantity FROM products WHERE id = ?", (product_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def get_all_products(order_by="brand"):
    conn = sqlite3.connect(db_path)  # Use the absolute path to the database
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, name, category, brand, price, quantity FROM products ORDER BY {order_by}")
    results = cursor.fetchall()
    conn.close()
    return results

def add_product_ui():
    def submit():
        product_id = entries["ID"].get()
        name = entries["Name"].get()
        category = entries["Category"].get()
        brand = entries["Brand"].get()
        price = entries["Price"].get()
        quantity = entries["Quantity"].get()
        if all([product_id.isdigit(), name, category, brand, price.replace('.', '', 1).isdigit(), quantity.isdigit()]):
            add_product_with_id(int(product_id), name, category, brand, float(price), int(quantity))
            messagebox.showinfo("Success", "Product added successfully")
            add_window.destroy()
        else:
            messagebox.showerror("Error", "Invalid input")

    add_window = tk.Toplevel(root)
    add_window.title("Add Product")

    fields = ["ID", "Name", "Category", "Brand", "Price", "Quantity"]
    entries = {}

    for i, field in enumerate(fields):
        tk.Label(add_window, text=f"{field}:").grid(row=i, column=0)
        entries[field] = tk.Entry(add_window)
        entries[field].grid(row=i, column=1)

    tk.Button(add_window, text="Submit", command=submit).grid(row=len(fields), column=0, columnspan=2)

def update_quantity_ui():
    def submit():
        product_id = id_entry.get()
        amount = amount_entry.get()
        if product_id.isdigit() and amount.lstrip('-').isdigit():
            update_quantity(int(product_id), int(amount))
            messagebox.showinfo("Success", "Quantity updated successfully")
            update_window.destroy()
        else:
            messagebox.showerror("Error", "Invalid input")

    update_window = tk.Toplevel(root)
    update_window.title("Update Quantity")

    tk.Label(update_window, text="Product ID:").grid(row=0, column=0)
    id_entry = tk.Entry(update_window)
    id_entry.grid(row=0, column=1)

    tk.Label(update_window, text="Amount (+/-):").grid(row=1, column=0)
    amount_entry = tk.Entry(update_window)
    amount_entry.grid(row=1, column=1)

    tk.Button(update_window, text="Submit", command=submit).grid(row=2, column=0, columnspan=2)

def check_stock_ui():
    def submit():
        product_id = id_entry.get()
        if product_id.isdigit():
            result = check_stock(int(product_id))
            if result:
                name, quantity = result
                messagebox.showinfo("Stock Information", f"Name: {name}\nQuantity: {quantity}")
            else:
                messagebox.showerror("Error", "Product not found")
            check_window.destroy()
        else:
            messagebox.showerror("Error", "Invalid input")

    check_window = tk.Toplevel(root)
    check_window.title("Check Stock")

    tk.Label(check_window, text="Product ID:").grid(row=0, column=0)
    id_entry = tk.Entry(check_window)
    id_entry.grid(row=0, column=1)

    tk.Button(check_window, text="Submit", command=submit).grid(row=1, column=0, columnspan=2)

def check_all_products_ui():
    def refresh_table(order_by):
        for widget in table_frame.winfo_children():
            widget.destroy()

        all_products = get_all_products(order_by)
        headers = ["ID", "Name", "Category", "Brand", "Price", "Quantity"]

        for col, header in enumerate(headers):
            tk.Label(table_frame, text=header).grid(row=0, column=col, padx=10, pady=5)

        for i, product in enumerate(all_products, start=1):
            for j, value in enumerate(product):
                tk.Label(table_frame, text=value if j != 4 else f"{value:.2f}").grid(row=i, column=j, padx=10, pady=5)

    all_window = tk.Toplevel(root)
    all_window.title("All Products")

    table_frame = tk.Frame(all_window)
    table_frame.pack()

    button_frame = tk.Frame(all_window)
    button_frame.pack()

    sort_options = ["Category", "Brand", "Price"]
    for i, option in enumerate(sort_options):
        tk.Button(button_frame, text=f"Sort by {option}", command=lambda opt=option.lower(): refresh_table(opt)).grid(row=0, column=i)

    refresh_table("brand")

def reset_database():
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"{db_path} has been reset.")
    else:
        print(f"{db_path} does not exist.")

# Main application setup
root = tk.Tk()
root.title("Inventory Management System")

menu = tk.Menu(root)
root.config(menu=menu)

product_menu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Products", menu=product_menu)
product_menu.add_command(label="Add Product", command=add_product_ui)
product_menu.add_command(label="Update Quantity", command=update_quantity_ui)
product_menu.add_command(label="Check Stock", command=check_stock_ui)
product_menu.add_command(label="View All Products", command=check_all_products_ui)

initialize_database()
root.mainloop()
