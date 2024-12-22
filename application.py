import sqlite3
import os
import tkinter as tk
from tkinter import messagebox


def initialize_database():
    conn = sqlite3.connect("inventory.db")
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
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO products (id, name, category, brand, price, quantity) VALUES (?, ?, ?, ?, ?, ?)",
                       (product_id, name, category, brand, price, quantity))
        conn.commit()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Product ID already exists")
    conn.close()


def update_quantity(product_id, amount):
    conn = sqlite3.connect("inventory.db")
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
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, quantity FROM products WHERE id = ?", (product_id,))
    result = cursor.fetchone()
    conn.close()
    return result


def get_all_products(order_by="brand"):
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, name, category, brand, price, quantity FROM products ORDER BY {order_by}")
    results = cursor.fetchall()
    conn.close()
    return results


def new_order_ui():
    def submit():
        product_id = id_entry.get()
        quantity = quantity_entry.get()
        if product_id.isdigit() and quantity.isdigit():
            quantity = int(quantity)
            if quantity > 0:
                update_quantity(int(product_id), -quantity)  # Decrease the specified quantity
                messagebox.showinfo("Success", f"Product quantity decreased by {quantity}")
                new_order_window.destroy()
            else:
                messagebox.showerror("Error", "Quantity must be greater than zero")
        else:
            messagebox.showerror("Error", "Invalid input")

    new_order_window = tk.Toplevel(root)
    new_order_window.title("New Order")

    tk.Label(new_order_window, text="Product ID:").grid(row=0, column=0)
    id_entry = tk.Entry(new_order_window)
    id_entry.grid(row=0, column=1)

    tk.Label(new_order_window, text="Quantity to Remove:").grid(row=1, column=0)
    quantity_entry = tk.Entry(new_order_window)
    quantity_entry.grid(row=1, column=1)

    tk.Button(new_order_window, text="Submit", command=submit).grid(row=2, column=0, columnspan=2)


def new_restock_ui():
    def submit():
        product_id = id_entry.get()
        quantity = quantity_entry.get()
        if product_id.isdigit() and quantity.isdigit():
            update_quantity(int(product_id), int(quantity))  # Add quantity
            messagebox.showinfo("Success", "Product restocked")
            new_restock_window.destroy()
        else:
            messagebox.showerror("Error", "Invalid input")

    new_restock_window = tk.Toplevel(root)
    new_restock_window.title("New Restock")

    tk.Label(new_restock_window, text="Product ID:").grid(row=0, column=0)
    id_entry = tk.Entry(new_restock_window)
    id_entry.grid(row=0, column=1)

    tk.Label(new_restock_window, text="Quantity to Add:").grid(row=1, column=0)
    quantity_entry = tk.Entry(new_restock_window)
    quantity_entry.grid(row=1, column=1)

    tk.Button(new_restock_window, text="Submit", command=submit).grid(row=2, column=0, columnspan=2)


def manage_ui(option):
    if option == "check_stock":
        def submit():
            product_id = id_entry.get()
            if product_id.isdigit():
                result = check_stock(int(product_id))
                if result:
                    name, quantity = result
                    messagebox.showinfo("Stock Information", f"Name: {name}\nQuantity: {quantity}")
                else:
                    messagebox.showerror("Error", "Product not found")
                manage_window.destroy()
            else:
                messagebox.showerror("Error", "Invalid input")

        manage_window = tk.Toplevel(root)
        manage_window.title("Check Stock")

        tk.Label(manage_window, text="Product ID:").grid(row=0, column=0)
        id_entry = tk.Entry(manage_window)
        id_entry.grid(row=0, column=1)

        tk.Button(manage_window, text="Submit", command=submit).grid(row=1, column=0, columnspan=2)

    elif option == "view_all":
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

        manage_window = tk.Toplevel(root)
        manage_window.title("View All Products")

        table_frame = tk.Frame(manage_window)
        table_frame.pack()

        button_frame = tk.Frame(manage_window)
        button_frame.pack()

        sort_options = ["Category", "Brand", "Price"]
        for i, option in enumerate(sort_options):
            tk.Button(button_frame, text=f"Sort by {option}", command=lambda opt=option.lower(): refresh_table(opt)).grid(row=0, column=i)

        refresh_table("brand")


# Main application setup
root = tk.Tk()
root.title("Inventory Management System")
root.geometry("800x600")  # Full screen size

# Create main layout (two vertical sections)
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

menu_frame = tk.Frame(main_frame, width=150, bg="lightgray")  # First vertical section (menu)
menu_frame.pack(side=tk.LEFT, fill=tk.Y)

content_frame = tk.Frame(main_frame, bg="white")  # Second vertical section (content)
content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Create menu
menu_button_new_order = tk.Button(menu_frame, text="New Order", command=lambda: new_order_ui())
menu_button_new_order.pack(fill=tk.X)

menu_button_new_restock = tk.Button(menu_frame, text="New Restock", command=lambda: new_restock_ui())
menu_button_new_restock.pack(fill=tk.X)

menu_button_manage = tk.Button(menu_frame, text="Manage", command=lambda: manage_ui("view_all"))
menu_button_manage.pack(fill=tk.X)

# Show the "View All" section by default
manage_ui("view_all")

initialize_database()
root.mainloop()
