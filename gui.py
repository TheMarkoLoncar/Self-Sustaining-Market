# gui.py

import tkinter as tk
from tkinter import ttk
from marketplace import submit_order, get_matches, get_current_price, get_product_list

def create_window(user_type):
    window = tk.Tk()
    window.title(user_type)

    # Labels
    tk.Label(window, text=f"{user_type} Interface", font=("Arial", 16)).pack(pady=10)

    tk.Label(window, text="Product:").pack()
    product_var = tk.StringVar(window)
    product_var.set(get_product_list()[0])
    product_dropdown = ttk.Combobox(window, textvariable=product_var, values=get_product_list(), state="readonly")
    product_dropdown.pack()

    tk.Label(window, text="Quantity:").pack()
    quantity_entry = tk.Entry(window)
    quantity_entry.pack()

    price_label = tk.Label(window, text="Price per unit (₦):")
    price_label.pack()
    price_value = tk.Label(window, text="")
    price_value.pack()

    result_label = tk.Label(window, text="", fg="green")
    result_label.pack(pady=5)

    # Match list
    match_box = tk.Listbox(window, width=50)
    match_box.pack(pady=10)

    def update_price_display(*args):
        product = product_var.get()
        price = get_current_price(product)
        price_value.config(text=f"₦{price:.2f}")

    def submit():
        product = product_var.get()
        quantity = quantity_entry.get()
        if not product or not quantity:
            result_label.config(text="Fill in all fields", fg="red")
            return
        try:
            order = submit_order(user_type, product, quantity)
            result_label.config(text=f"{order.quantity} {order.product} order placed at ₦{order.price:.2f}", fg="green")
            update_matches()
            update_price_display()
        except Exception as e:
            result_label.config(text=str(e), fg="red")

    def update_matches():
        match_box.delete(0, tk.END)
        for m in get_matches():
            match_box.insert(tk.END, m)

    product_var.trace("w", update_price_display)
    update_price_display()

    tk.Button(window, text="Submit Order", command=submit).pack(pady=5)
    tk.Button(window, text="Refresh Matches", command=update_matches).pack(pady=5)

    return window

# Create separate windows
if __name__ == "__main__":
    farmer_window = create_window("Farmer")
    buyer_window = create_window("Buyer")

    # Position side by side
    farmer_window.geometry("+100+100")
    buyer_window.geometry("+700+100")

    farmer_window.mainloop()
