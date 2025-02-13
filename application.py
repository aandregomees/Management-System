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

def search_products(criteria, term):
    conn = sqlite3.connect("/home/agomes/Desktop/FisioMove/inventory.db")
    cursor = conn.cursor()
    
    # Construct the SQL query based on the search criteria
    if criteria == "id":
        cursor.execute("SELECT * FROM products WHERE id = ?", (term,))
    elif criteria == "name":
        cursor.execute("SELECT * FROM products WHERE name LIKE ?", (f"%{term}%",))
    elif criteria == "category":
        cursor.execute("SELECT * FROM products WHERE category LIKE ?", (f"%{term}%",))
    elif criteria == "brand":
        cursor.execute("SELECT * FROM products WHERE brand LIKE ?", (f"%{term}%",))
    
    results = cursor.fetchall()
    conn.close()
    return results

def search_product_ui():
    # Clear the current content
    clear_content_area()
    
    # Create a frame for the search UI
    search_frame = tk.Frame(content_frame)
    search_frame.pack(pady=20)
    
    # Label and entry for search criteria
    tk.Label(search_frame, text="Search by:").grid(row=0, column=0, pady=5)
    search_criteria = tk.StringVar(value="id")  # Default search criteria
    search_options = ["id", "name", "category", "brand"]
    search_dropdown = tk.OptionMenu(search_frame, search_criteria, *search_options)
    search_dropdown.grid(row=0, column=1, pady=5)
    
    tk.Label(search_frame, text="Search term:").grid(row=1, column=0, pady=5)
    search_term_entry = tk.Entry(search_frame)
    search_term_entry.grid(row=1, column=1, pady=5)
    
    # Frame to display search results
    results_frame = tk.Frame(content_frame)
    results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def perform_search():
        # Clear previous results
        for widget in results_frame.winfo_children():
            widget.destroy()
        
        # Get the search criteria and term
        criteria = search_criteria.get()
        term = search_term_entry.get()
        
        if not term:
            messagebox.showerror("Error", "Please enter a search term.")
            return
        
        # Fetch products based on the search criteria
        products = search_products(criteria, term)
        
        if not products:
            tk.Label(results_frame, text="No products found.").pack(pady=10)
            return
        
        # Display the search results
        headers = ["ID", "Name", "Category", "Brand", "Price", "Quantity"]
        for i, header in enumerate(headers):
            tk.Label(results_frame, text=header, width=15, anchor="w").grid(row=0, column=i, padx=5, pady=5)
        
        for i, product in enumerate(products, start=1):
            for j, value in enumerate(product):
                tk.Label(results_frame, text=value if j != 4 else f"{value:.2f}", width=15, anchor="w").grid(row=i, column=j, padx=5, pady=5)
    
    # Button to perform the search
    tk.Button(search_frame, text="Search", command=perform_search).grid(row=2, column=0, columnspan=2, pady=10)
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
    order_items = []  # List to store products added to the order

    # Main frame for the order page
    order_frame = tk.Frame(content_frame)
    order_frame.pack(fill=tk.BOTH, expand=True)

    # Frame for the search bar
    search_frame = tk.Frame(order_frame)
    search_frame.pack(fill=tk.X, padx=10, pady=10)

    # Search criteria dropdown
    tk.Label(search_frame, text="Search by:").grid(row=0, column=0, padx=5, pady=5)
    search_criteria = tk.StringVar(value="name")  # Default search criteria
    search_options = ["id", "name", "category", "brand"]
    search_dropdown = tk.OptionMenu(search_frame, search_criteria, *search_options)
    search_dropdown.grid(row=0, column=1, padx=5, pady=5)

    # Search term entry
    tk.Label(search_frame, text="Search term:").grid(row=0, column=2, padx=5, pady=5)
    search_term_entry = tk.Entry(search_frame, width=30)
    search_term_entry.grid(row=0, column=3, padx=5, pady=5)

    # Button to perform the search
    def perform_search():
        # Clear previous search results
        for widget in results_frame.winfo_children():
            widget.destroy()

        # Get the search criteria and term
        criteria = search_criteria.get()
        term = search_term_entry.get()

        if not term:
            messagebox.showerror("Error", "Please enter a search term.")
            return

        # Fetch products based on the search criteria
        products = search_products(criteria, term)

        if not products:
            tk.Label(results_frame, text="No products found.").pack(pady=10)
            return

        # Display the search results
        for i, product in enumerate(products):
            product_id, name, category, brand, price, quantity = product
            product_text = f"{name}, Brand: {brand}, Price: {price:.2f}"
            product_button = tk.Button(results_frame, text=product_text, width=80, anchor="w",
                                       command=lambda p=product: add_to_order(p))
            product_button.pack(pady=2, padx=10, anchor="w")

    tk.Button(search_frame, text="Search", command=perform_search).grid(row=0, column=4, padx=5, pady=5)

    # Frame to display search results
    results_frame = tk.Frame(order_frame)
    results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Function to add a product to the order
    def add_to_order(product):
        product_id, name, _, _, _, _ = product

        # Open a new window to input quantity
        quantity_window = tk.Toplevel()
        quantity_window.title("Add to Order")
        quantity_window.geometry("300x150")

        tk.Label(quantity_window, text=f"Product: {name}").pack(pady=10)
        tk.Label(quantity_window, text="Quantity:").pack(pady=5)
        quantity_entry = tk.Entry(quantity_window)
        quantity_entry.pack(pady=5)

        def confirm_quantity():
            quantity = quantity_entry.get()
            if quantity.isdigit() and int(quantity) > 0:
                order_items.append((product_id, int(quantity)))
                order_listbox.insert(tk.END, f"ID: {product_id}, Quantity: {quantity}")
                quantity_window.destroy()
            else:
                messagebox.showerror("Error", "Please enter a valid quantity.")

        tk.Button(quantity_window, text="Add", command=confirm_quantity).pack(pady=10)

    # Frame to display the current order
    order_list_frame = tk.Frame(order_frame)
    order_list_frame.pack(fill=tk.X, padx=10, pady=10)

    tk.Label(order_list_frame, text="Current Order:").pack(anchor="w")
    order_listbox = tk.Listbox(order_list_frame, height=10, width=100)
    order_listbox.pack(fill=tk.X, pady=5)

    # Button to submit the order
    def submit_order():
        for product_id, quantity in order_items:
            update_quantity(int(product_id), -quantity)  # Decrease the quantity in the database
        messagebox.showinfo("Success", "Order has been processed.")
        order_frame.destroy()  # Close the current order frame

    tk.Button(order_list_frame, text="Submit Order", command=submit_order).pack(pady=10)
# New restock UI
def new_restock_ui():
    clear_content_area()
    restock_items = []  # List to store products added to the restock

    # Main frame for the restock page
    restock_frame = tk.Frame(content_frame)
    restock_frame.pack(fill=tk.BOTH, expand=True)

    # Frame for the search bar
    search_frame = tk.Frame(restock_frame)
    search_frame.pack(fill=tk.X, padx=10, pady=10)

    # Search criteria dropdown
    tk.Label(search_frame, text="Search by:").grid(row=0, column=0, padx=5, pady=5)
    search_criteria = tk.StringVar(value="name")  # Default search criteria
    search_options = ["id", "name", "category", "brand"]
    search_dropdown = tk.OptionMenu(search_frame, search_criteria, *search_options)
    search_dropdown.grid(row=0, column=1, padx=5, pady=5)

    # Search term entry
    tk.Label(search_frame, text="Search term:").grid(row=0, column=2, padx=5, pady=5)
    search_term_entry = tk.Entry(search_frame, width=30)
    search_term_entry.grid(row=0, column=3, padx=5, pady=5)

    # Button to perform the search
    def perform_search():
        # Clear previous search results
        for widget in results_frame.winfo_children():
            widget.destroy()

        # Get the search criteria and term
        criteria = search_criteria.get()
        term = search_term_entry.get()

        if not term:
            messagebox.showerror("Error", "Please enter a search term.")
            return

        # Fetch products based on the search criteria
        products = search_products(criteria, term)

        if not products:
            tk.Label(results_frame, text="No products found.").pack(pady=10)
            return

        # Display the search results
        for i, product in enumerate(products):
            product_id, name, category, brand, price, quantity = product
            product_text = f"{name}, Brand: {brand}, Price: {price:.2f}"
            product_button = tk.Button(results_frame, text=product_text, width=80, anchor="w",
                                       command=lambda p=product: add_to_restock(p))
            product_button.pack(pady=2, padx=10, anchor="w")

    tk.Button(search_frame, text="Search", command=perform_search).grid(row=0, column=4, padx=5, pady=5)

    # Frame to display search results
    results_frame = tk.Frame(restock_frame)
    results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Function to add a product to the restock
    def add_to_restock(product):
        product_id, name, _, _, _, _ = product

        # Open a new window to input quantity
        quantity_window = tk.Toplevel()
        quantity_window.title("Add to Restock")
        quantity_window.geometry("300x150")

        tk.Label(quantity_window, text=f"Product: {name}").pack(pady=10)
        tk.Label(quantity_window, text="Quantity:").pack(pady=5)
        quantity_entry = tk.Entry(quantity_window)
        quantity_entry.pack(pady=5)

        def confirm_quantity():
            quantity = quantity_entry.get()
            if quantity.isdigit() and int(quantity) > 0:
                restock_items.append((product_id, int(quantity)))
                restock_listbox.insert(tk.END, f"ID: {product_id}, Quantity: {quantity}")
                quantity_window.destroy()
            else:
                messagebox.showerror("Error", "Please enter a valid quantity.")

        tk.Button(quantity_window, text="Add", command=confirm_quantity).pack(pady=10)

    # Frame to display the current restock
    restock_list_frame = tk.Frame(restock_frame)
    restock_list_frame.pack(fill=tk.X, padx=10, pady=10)

    tk.Label(restock_list_frame, text="Current Restock:").pack(anchor="w")
    restock_listbox = tk.Listbox(restock_list_frame, height=10, width=100)
    restock_listbox.pack(fill=tk.X, pady=5)

    # Button to submit the restock
    def submit_restock():
        for product_id, quantity in restock_items:
            update_quantity(int(product_id), quantity)  # Increase the quantity in the database
        messagebox.showinfo("Success", "Restock has been processed.")
        restock_frame.destroy()  # Close the current restock frame

    tk.Button(restock_list_frame, text="Submit Restock", command=submit_restock).pack(pady=10)
# Function to retrieve paginated products
def get_paginated_products(order_by, offset, limit):
    conn = sqlite3.connect("/home/agomes/Desktop/FisioMove/inventory.db")
    cursor = conn.cursor()
    cursor.execute(f"""SELECT id, name, category, brand, price, quantity 
                     FROM products ORDER BY {order_by} LIMIT ? OFFSET ?""", (limit, offset))
    results = cursor.fetchall()
    conn.close()
    return results

def view_all_products_ui():
    clear_content_area()
    
    current_sort = tk.StringVar(value="brand")  # Default sort order
    current_page = tk.IntVar(value=0)  # Current page index
    items_per_page = 20  # Items per page

    products_frame = tk.Frame(content_frame)
    products_frame.pack(fill=tk.BOTH, expand=True)

    # Frame for sorting buttons
    sort_frame = tk.Frame(products_frame)
    sort_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

    # Sorting buttons
    tk.Button(sort_frame, text="Sort by ID", command=lambda: sort_by("id")).pack(pady=5)
    tk.Button(sort_frame, text="Sort by Name", command=lambda: sort_by("name")).pack(pady=5)
    tk.Button(sort_frame, text="Sort by Category", command=lambda: sort_by("category")).pack(pady=5)
    tk.Button(sort_frame, text="Sort by Brand", command=lambda: sort_by("brand")).pack(pady=5)
    tk.Button(sort_frame, text="Sort by Price", command=lambda: sort_by("price")).pack(pady=5)

    # Frame for the product list
    inner_frame = tk.Frame(products_frame)
    inner_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def populate_products():
        offset = current_page.get() * items_per_page
        products = get_paginated_products(current_sort.get(), offset, items_per_page)

        for widget in inner_frame.winfo_children():
            widget.destroy()

        headers = ["ID", "Name", "Category", "Brand", "Price", "Quantity"]
        for i, header in enumerate(headers):
            tk.Label(inner_frame, text=header, width=15, anchor="w").grid(row=0, column=i, padx=5, pady=5)

        for i, product in enumerate(products, start=1):
            for j, value in enumerate(product):
                tk.Label(inner_frame, text=value if j != 4 else f"{value:.2f}", width=15, anchor="w").grid(row=i, column=j, padx=5, pady=5)

        navigation_frame = tk.Frame(inner_frame)
        navigation_frame.grid(row=items_per_page + 2, column=0, columnspan=6, pady=10)
        
        prev_button = tk.Button(navigation_frame, text="Previous", command=lambda: navigate_page(-1))
        next_button = tk.Button(navigation_frame, text="Next", command=lambda: navigate_page(1))
        
        if current_page.get() > 0:
            prev_button.pack(side=tk.LEFT, padx=5)
        if len(products) == items_per_page:
            next_button.pack(side=tk.RIGHT, padx=5)
        
        tk.Label(navigation_frame, text=f"Page {current_page.get() + 1}").pack(side=tk.LEFT, padx=10)

    def navigate_page(direction):
        new_page = current_page.get() + direction
        if new_page >= 0:
            current_page.set(new_page)
            populate_products()
    
    def sort_by(order_by):
        current_sort.set(order_by)
        current_page.set(0)
        populate_products()
    
    populate_products()
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
