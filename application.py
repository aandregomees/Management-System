import sqlite3
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
    order_items = []
    order_frame = tk.Frame(content_frame)
    order_frame.pack(fill=tk.BOTH, expand=True)

    def add_product():
        product_id = id_entry.get()
        quantity = quantity_entry.get()
        
        if product_id.isdigit() and quantity.isdigit():
            quantity = int(quantity)
            if quantity > 0:
                result = check_stock(int(product_id))
                if result:
                    name, available_quantity = result
                    if available_quantity >= quantity:
                        order_items.append((product_id, quantity))
                        order_listbox.insert(tk.END, f"ID: {product_id}, Quantity: {quantity}")
                    else:
                        messagebox.showerror("Error", "Insufficient stock")
                else:
                    messagebox.showerror("Error", "Product not found")
            else:
                messagebox.showerror("Error", "Quantity must be greater than zero")
        else:
            messagebox.showerror("Error", "Invalid input")
    
    def submit_order():
        for product_id, quantity in order_items:
            update_quantity(int(product_id), -quantity)  # Decrease the specified quantity
        messagebox.showinfo("Success", "Order has been processed")
        order_frame.destroy()  # Close the current order frame

    # Increase the width of the entries and buttons
    tk.Label(order_frame, text="Product ID:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    id_entry = tk.Entry(order_frame, width=40)  # Increase width here
    id_entry.grid(row=0, column=0, padx=70, pady=5)

    tk.Label(order_frame, text="Quantity:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    quantity_entry = tk.Entry(order_frame, width=40)  # Increase width here
    quantity_entry.grid(row=1, column=0, padx=70, pady=5)

    tk.Button(order_frame, text="Add Product to Order", command=add_product).grid(row=2, column=0, columnspan=2, pady=10)

    tk.Button(order_frame, text="Submit Order", command=submit_order).grid(row=3, column=0, columnspan=2, pady=10)

    # Increased width for listbox to display more data in the new order section
    order_listbox = tk.Listbox(order_frame, height=10, width=100)  # Increase width here
    order_listbox.grid(row=4, column=0, columnspan=2, padx=10, pady=5)


# New restock UI in the same window
def new_restock_ui():
    restock_items = []
    restock_frame = tk.Frame(content_frame)
    restock_frame.pack(fill=tk.BOTH, expand=True)

    def add_product():
        product_id = id_entry.get()
        quantity = quantity_entry.get()
        
        if product_id.isdigit() and quantity.isdigit():
            quantity = int(quantity)
            if quantity > 0:
                result = check_stock(int(product_id))
                if result:
                    name, available_quantity = result
                    # If the product exists, just add the quantity to restock
                    restock_items.append((product_id, quantity))
                    restock_listbox.insert(tk.END, f"ID: {product_id}, Quantity: {quantity}")
                else:
                    messagebox.showerror("Error", "Product not found")
            else:
                messagebox.showerror("Error", "Quantity must be greater than zero")
        else:
            messagebox.showerror("Error", "Invalid input")
    
    def submit_restock():
        for product_id, quantity in restock_items:
            update_quantity(int(product_id), quantity)  # Increase the specified quantity
        messagebox.showinfo("Success", "Restock has been processed")
        restock_frame.destroy()  # Close the current restock frame

    # Increase the width of the entries and buttons
    tk.Label(restock_frame, text="Product ID:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    id_entry = tk.Entry(restock_frame, width=40)  # Increase width here
    id_entry.grid(row=0, column=0, padx=70, pady=5)

    tk.Label(restock_frame, text="Quantity to Add:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    quantity_entry = tk.Entry(restock_frame, width=40)  # Increase width here
    quantity_entry.grid(row=1, column=0, padx=70, pady=5)

    tk.Button(restock_frame, text="Add Product to Restock", command=add_product).grid(row=2, column=0, columnspan=2, pady=10)

    tk.Button(restock_frame, text="Submit Restock", command=submit_restock).grid(row=3, column=0, columnspan=2, pady=10)

    # Increased width for listbox to display more data in the new restock section
    restock_listbox = tk.Listbox(restock_frame, height=10, width=100)  # Increase width here
    restock_listbox.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

# Manage products UI in the same window
def manage_ui(option):
    manage_frame = tk.Frame(content_frame)
    manage_frame.pack(fill=tk.BOTH, expand=True)

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
                manage_frame.destroy()
            else:
                messagebox.showerror("Error", "Invalid input")

        tk.Label(manage_frame, text="Product ID:").grid(row=0, column=0)
        id_entry = tk.Entry(manage_frame)
        id_entry.grid(row=0, column=1)

        tk.Button(manage_frame, text="Submit", command=submit).grid(row=1, column=0, columnspan=2)

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

        tk.Label(manage_frame, text="Sort by:").grid(row=0, column=0)
        button_frame = tk.Frame(manage_frame)
        button_frame.grid(row=0, column=1)

        sort_options = ["Category", "Brand", "Price"]
        for i, option in enumerate(sort_options):
            tk.Button(button_frame, text=f"Sort by {option}", command=lambda opt=option.lower(): refresh_table(opt)).grid(row=0, column=i)

        table_frame = tk.Frame(manage_frame)
        table_frame.grid(row=1, column=0, columnspan=2)

        refresh_table("brand")

# Update the content section
def update_content(content_function):
    for widget in content_frame.winfo_children():
        widget.destroy()

    content_function()

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
menu_button_new_order = tk.Button(menu_frame, text="New Order", command=lambda: update_content(new_order_ui))
menu_button_new_order.pack(fill=tk.X)

menu_button_new_restock = tk.Button(menu_frame, text="New Restock", command=lambda: update_content(new_restock_ui))
menu_button_new_restock.pack(fill=tk.X)

menu_button_manage = tk.Button(menu_frame, text="Manage Products", command=lambda: update_content(lambda: manage_ui("view_all")))
menu_button_manage.pack(fill=tk.X)

menu_button_view_all = tk.Button(menu_frame, text="View All Products", command=lambda: update_content(lambda: manage_ui("view_all")))
menu_button_view_all.pack(fill=tk.X)

# Show the "View All" section by default
update_content(lambda: manage_ui("view_all"))

initialize_database()
root.mainloop()
