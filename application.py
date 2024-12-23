import sqlite3
import tkinter as tk
from tkinter import messagebox

def initialize_database():
    conn = sqlite3.connect("/home/agomes/Desktop/FisioMove/inventory.db")
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

# Function to add product to database
def add_product_with_id(product_id, name, category, brand, price, quantity):
    conn = sqlite3.connect("/home/agomes/Desktop/FisioMove/inventory.db")
    cursor = conn.cursor()
    try:
        # Round the price to two decimals before inserting
        price = round(price, 2)
        cursor.execute("INSERT INTO products (id, name, category, brand, price, quantity) VALUES (?, ?, ?, ?, ?, ?)",
                       (product_id, name, category, brand, price, quantity))
        conn.commit()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Product ID already exists")
    conn.close()
# Function for "Create New Product" UI
def new_product_ui():
    # Clear the current content
    clear_content_area()
    
    # Create a frame for new product UI
    new_product_frame = tk.Frame(content_frame)
    new_product_frame.pack(pady=20)
    
    # Add labels and entry fields for product details
    tk.Label(new_product_frame, text="Product ID:").grid(row=0, column=0, pady=5)
    product_id_entry = tk.Entry(new_product_frame)
    product_id_entry.grid(row=0, column=1, pady=5)
    
    tk.Label(new_product_frame, text="Product Name:").grid(row=1, column=0, pady=5)
    product_name_entry = tk.Entry(new_product_frame)
    product_name_entry.grid(row=1, column=1, pady=5)
    
    tk.Label(new_product_frame, text="Category:").grid(row=2, column=0, pady=5)
    category_entry = tk.Entry(new_product_frame)
    category_entry.grid(row=2, column=1, pady=5)
    
    tk.Label(new_product_frame, text="Brand:").grid(row=3, column=0, pady=5)
    brand_entry = tk.Entry(new_product_frame)
    brand_entry.grid(row=3, column=1, pady=5)
    
    tk.Label(new_product_frame, text="Price:").grid(row=4, column=0, pady=5)
    price_entry = tk.Entry(new_product_frame)
    price_entry.grid(row=4, column=1, pady=5)
    
    tk.Label(new_product_frame, text="Quantity:").grid(row=5, column=0, pady=5)
    quantity_entry = tk.Entry(new_product_frame)
    quantity_entry.grid(row=5, column=1, pady=5)

    # Submit button to add the new product
    def submit_new_product():
        product_id = product_id_entry.get()
        product_name = product_name_entry.get()
        category = category_entry.get()
        brand = brand_entry.get()
        price = price_entry.get()
        quantity = quantity_entry.get()
        
        # Validation check for all fields
        if not (product_id.isdigit() and price.replace('.', '', 1).isdigit() and quantity.isdigit()):
            messagebox.showerror("Invalid Input", "Please enter valid values for Product ID, Price, and Quantity.")
            return
        
        # Round the price to two decimal places
        price = round(float(price), 2)
        
        # Add the product to the database
        add_product_with_id(product_id, product_name, category, brand, price, int(quantity))
        
        # Confirmation message
        tk.Label(new_product_frame, text="Product successfully added!").grid(row=6, column=0, columnspan=2, pady=10)

    tk.Button(new_product_frame, text="Add Product", command=submit_new_product).grid(row=6, column=0, columnspan=2, pady=10)


def update_quantity(product_id, amount):
    conn = sqlite3.connect("/home/agomes/Desktop/FisioMove/inventory.db")
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
    conn = sqlite3.connect("/home/agomes/Desktop/FisioMove/inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, quantity FROM products WHERE id = ?", (product_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def get_all_products(order_by="brand"):
    conn = sqlite3.connect("/home/agomes/Desktop/FisioMove/inventory.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, name, category, brand, price, quantity FROM products ORDER BY {order_by}")
    results = cursor.fetchall()
    conn.close()
    return results

# New order UI
def new_order_ui():
    clear_content_area()
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

    tk.Label(order_frame, text="Product ID:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    id_entry = tk.Entry(order_frame, width=40)  
    id_entry.grid(row=0, column=0, padx=70, pady=5)

    tk.Label(order_frame, text="Quantity:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    quantity_entry = tk.Entry(order_frame, width=40)  
    quantity_entry.grid(row=1, column=0, padx=70, pady=5)

    tk.Button(order_frame, text="Add Product to Order", command=add_product).grid(row=2, column=0, columnspan=2, pady=10)

    tk.Button(order_frame, text="Submit Order", command=submit_order).grid(row=3, column=0, columnspan=2, pady=10)

    order_listbox = tk.Listbox(order_frame, height=10, width=100)
    order_listbox.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

# New restock UI
def new_restock_ui():
    clear_content_area()
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
            update_quantity(int(product_id), quantity)  
        messagebox.showinfo("Success", "Restock has been processed")
        restock_frame.destroy()

    tk.Label(restock_frame, text="Product ID:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    id_entry = tk.Entry(restock_frame, width=40)  
    id_entry.grid(row=0, column=0, padx=70, pady=5)

    tk.Label(restock_frame, text="Quantity to Add:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    quantity_entry = tk.Entry(restock_frame, width=40)  
    quantity_entry.grid(row=1, column=0, padx=70, pady=5)

    tk.Button(restock_frame, text="Add Product to Restock", command=add_product).grid(row=2, column=0, columnspan=2, pady=10)

    tk.Button(restock_frame, text="Submit Restock", command=submit_restock).grid(row=3, column=0, columnspan=2, pady=10)

    restock_listbox = tk.Listbox(restock_frame, height=10, width=100)
    restock_listbox.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

# View all products UI
def view_all_products_ui():
    clear_content_area()
    products_frame = tk.Frame(content_frame)
    products_frame.pack(fill=tk.BOTH, expand=True)

    products = get_all_products()

    tk.Label(products_frame, text="ID", width=10, anchor="w").grid(row=0, column=0, padx=10, pady=5)
    tk.Label(products_frame, text="Name", width=20, anchor="w").grid(row=0, column=1, padx=10, pady=5)
    tk.Label(products_frame, text="Category", width=20, anchor="w").grid(row=0, column=2, padx=10, pady=5)
    tk.Label(products_frame, text="Brand", width=20, anchor="w").grid(row=0, column=3, padx=10, pady=5)
    tk.Label(products_frame, text="Price", width=10, anchor="w").grid(row=0, column=4, padx=10, pady=5)
    tk.Label(products_frame, text="Quantity", width=10, anchor="w").grid(row=0, column=5, padx=10, pady=5)

    for i, product in enumerate(products, start=1):
        for j, value in enumerate(product):
            tk.Label(products_frame, text=value if j != 4 else f"{value:.2f}", width=20, anchor="w").grid(row=i, column=j, padx=10, pady=5)

# Manage products UI (with Add, Edit, and Search options)
def manage_ui():
    clear_content_area()
    manage_frame = tk.Frame(content_frame)
    manage_frame.pack(fill=tk.BOTH, expand=True)

    def show_manage_options():
        for widget in manage_frame.winfo_children():
            widget.destroy()

        tk.Button(manage_frame, text="Search Product", command=lambda: show_process("search_product")).pack(pady=10)
        tk.Button(manage_frame, text="Edit Product", command=lambda: show_process("edit_product")).pack(pady=10)
        tk.Button(manage_frame, text="Create New Product", command=lambda: show_process("new_product")).pack(pady=10)


    def show_process(option):
        clear_content_area()
        if option == "search_product":
            search_product_ui()
        elif option == "edit_product":
            edit_product_ui()
        elif option == "new_product":
            new_product_ui()  

    show_manage_options()

def search_product_ui():
    manage_frame = tk.Frame(content_frame)
    manage_frame.pack(fill=tk.BOTH, expand=True)

    def submit_search():
        search_value = search_entry.get()
        if search_value:
            conn = sqlite3.connect("/home/agomes/Desktop/FisioMove/inventory.db")
            cursor = conn.cursor()

            if search_value.isdigit():  # Search by ID
                cursor.execute("SELECT * FROM products WHERE id = ?", (search_value,))
            else:  # Search by Name (or part of it)
                cursor.execute("SELECT * FROM products WHERE name LIKE ? OR category LIKE ? OR brand LIKE ?",
                               (f"%{search_value}%", f"%{search_value}%", f"%{search_value}%"))
            
            results = cursor.fetchall()
            conn.close()

            if results:
                for widget in search_table.winfo_children():
                    widget.destroy()
                headers = ["ID", "Name", "Category", "Brand", "Price", "Quantity"]
                for col, header in enumerate(headers):
                    tk.Label(search_table, text=header).grid(row=0, column=col, padx=10, pady=5)
                for i, product in enumerate(results, start=1):
                    for j, value in enumerate(product):
                        tk.Label(search_table, text=value if j != 4 else f"{value:.2f}").grid(row=i, column=j, padx=10, pady=5)
            else:
                messagebox.showinfo("No Results", "No products found matching your search.")

    tk.Label(manage_frame, text="Search by ID, Name, Category, or Brand:").grid(row=0, column=0, padx=10, pady=5)
    search_entry = tk.Entry(manage_frame)
    search_entry.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(manage_frame, text="Search", command=submit_search).grid(row=0, column=2, padx=10, pady=5)

    search_table = tk.Frame(manage_frame)
    search_table.grid(row=1, column=0, columnspan=3, padx=10, pady=5)

# Edit Product UI
def edit_product_ui():
    # Clear the current content
    clear_content_area()
    
    # Create a frame for editing product UI
    edit_product_frame = tk.Frame(content_frame)
    edit_product_frame.pack(pady=20)
    
    # Label and entry for the product ID (to identify the product to edit)
    tk.Label(edit_product_frame, text="Enter Product ID to Edit:").grid(row=0, column=0, pady=5)
    product_id_entry = tk.Entry(edit_product_frame)
    product_id_entry.grid(row=0, column=1, pady=5)
    
    # Button to load product details based on ID
    def load_product_details():
        product_id = product_id_entry.get()
        
        # Fetch product details based on the ID
        product = get_product_by_id(product_id)  # This function should fetch product from DB
        
        if product:
            # Pre-fill the fields with the current product data
            product_name_entry.delete(0, tk.END)
            product_name_entry.insert(0, product[1])  # Assuming product[1] is name
            
            category_entry.delete(0, tk.END)
            category_entry.insert(0, product[2])  # Assuming product[2] is category
            
            brand_entry.delete(0, tk.END)
            brand_entry.insert(0, product[3])  # Assuming product[3] is brand
            
            price_entry.delete(0, tk.END)
            price_entry.insert(0, product[4])  # Assuming product[4] is price
            
            # Show quantity in a label (can't be edited)
            quantity_label.config(text=f"Quantity: {product[5]}")  # Assuming product[5] is quantity
            
            # Optionally, show a confirmation message
            tk.Label(edit_product_frame, text="Product details loaded!").grid(row=6, column=0, columnspan=2, pady=10)
        else:
            # Handle case where product is not found
            tk.Label(edit_product_frame, text="Product not found!").grid(row=6, column=0, columnspan=2, pady=10)

    tk.Button(edit_product_frame, text="Load Product", command=load_product_details).grid(row=1, column=0, columnspan=2, pady=10)
    
    # Entry fields for editable product details (excluding quantity)
    tk.Label(edit_product_frame, text="Product Name:").grid(row=2, column=0, pady=5)
    product_name_entry = tk.Entry(edit_product_frame)
    product_name_entry.grid(row=2, column=1, pady=5)
    
    tk.Label(edit_product_frame, text="Category:").grid(row=3, column=0, pady=5)
    category_entry = tk.Entry(edit_product_frame)
    category_entry.grid(row=3, column=1, pady=5)
    
    tk.Label(edit_product_frame, text="Brand:").grid(row=4, column=0, pady=5)
    brand_entry = tk.Entry(edit_product_frame)
    brand_entry.grid(row=4, column=1, pady=5)
    
    tk.Label(edit_product_frame, text="Price:").grid(row=5, column=0, pady=5)
    price_entry = tk.Entry(edit_product_frame)
    price_entry.grid(row=5, column=1, pady=5)
    
    # Display quantity (cannot be edited)
    quantity_label = tk.Label(edit_product_frame, text="Quantity: N/A")
    quantity_label.grid(row=6, column=0, columnspan=2, pady=5)

    # Submit button to save the edited product
    def submit_edited_product():
        product_id = product_id_entry.get()
        product_name = product_name_entry.get()
        category = category_entry.get()
        brand = brand_entry.get()
        price = price_entry.get()
        
        # Validation for the fields
        if not product_name or not category or not brand or not price:
            messagebox.showerror("Invalid Input", "Please provide valid product details.")
            return
        
        # Validate if the price is a valid float
        try:
            price = float(price)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please provide a valid price.")
            return
        
        # Round the price to two decimal places
        price = round(price, 2)
        
        # Save the edited product (excluding quantity)
        update_product(product_id, product_name, category, brand, price)  # Function to update product in DB
        
        # Optionally, show a confirmation message or return to the main screen
        tk.Label(edit_product_frame, text="Product successfully updated!").grid(row=7, column=0, columnspan=2, pady=10)

    tk.Button(edit_product_frame, text="Update Product", command=submit_edited_product).grid(row=7, column=0, columnspan=2, pady=10)

# Function to update the product in the database (excluding quantity)
def update_product(product_id, product_name, category, brand, price):
    conn = sqlite3.connect("/home/agomes/Desktop/FisioMove/inventory.db")
    cursor = conn.cursor()
    cursor.execute('''UPDATE products
                      SET name = ?, category = ?, brand = ?, price = ?
                      WHERE id = ?''', (product_name, category, brand, price, product_id))
    conn.commit()
    conn.close()

# Function to fetch a product by ID
def get_product_by_id(product_id):
    conn = sqlite3.connect("/home/agomes/Desktop/FisioMove/inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()  # Fetch one product by ID
    conn.close()
    return product
# Main UI Setup
def clear_content_area():
    for widget in content_frame.winfo_children():
        widget.destroy()

root = tk.Tk()
root.title("Inventory Management")
root.geometry("1200x800")

main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

sidebar_frame = tk.Frame(main_frame, width=200, bg="lightgray")
sidebar_frame.grid(row=0, column=0, sticky="nswe")

content_frame = tk.Frame(main_frame)
content_frame.grid(row=0, column=1, sticky="nswe")

# Sidebar buttons
tk.Button(sidebar_frame, text="Manage Products", command=manage_ui).pack(fill=tk.X, padx=10, pady=5)
tk.Button(sidebar_frame, text="New Order", command=new_order_ui).pack(fill=tk.X, padx=10, pady=5)
tk.Button(sidebar_frame, text="Restock", command=new_restock_ui).pack(fill=tk.X, padx=10, pady=5)
tk.Button(sidebar_frame, text="View All Products", command=view_all_products_ui).pack(fill=tk.X, padx=10, pady=5)

# Initialize the database
initialize_database()

root.mainloop()
