import tkinter as tk
from tkinter import ttk
from marketplace import (
    submit_order, get_matches, get_current_price,
    get_product_list, get_wallet, get_inventory
)

order_windows = []

def create_order_window(order_type, product, quantity, price):
    win = tk.Toplevel()
    win.title(f"{order_type.upper()} ORDER")

    var_text = tk.StringVar()
    var_text.set(f"{quantity}kg of {product.upper()} at ₦{price:.2f}/kg, 0/{quantity}kg filled")

    label = tk.Label(win, textvariable=var_text, font=("Arial", 12))
    label.pack(padx=10, pady=10)

    cleared = [False]

    def update_progress(current_fill):
        if cleared[0]:
            return
        if current_fill >= quantity:
            var_text.set(f"{quantity}kg of {product.upper()} at ₦{price:.2f}/kg, {quantity}/{quantity}kg filled")
            label.config(fg="green")
            btn = tk.Button(win, text="Clear", command=lambda: (win.destroy(), order_windows.remove(win)))
            btn.pack(pady=5)
            cleared[0] = True
        else:
            var_text.set(f"{quantity}kg of {product.upper()} at ₦{price:.2f}/kg, {current_fill}/{quantity}kg filled")

    order_windows.append(win)
    return update_progress

def create_window(user_type):
    window = tk.Tk()
    window.title(user_type)

    tk.Label(window, text=f"{user_type} Interface", font=("Arial", 16)).pack(pady=10)

    wallet_var = tk.StringVar()
    inventory_text = tk.StringVar()

    def refresh_wallet_inventory():
        wallet_var.set(f"Wallet: ₦{get_wallet(user_type):,.2f}")
        if user_type == "Farmer":
            inventory = get_inventory()
            inventory_text.set("Inventory: " + ", ".join(f"{k}: {v}kg" for k, v in inventory.items()))

    tk.Label(window, textvariable=wallet_var).pack()
    if user_type == "Farmer":
        tk.Label(window, textvariable=inventory_text).pack()
    refresh_wallet_inventory()

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
            price = get_current_price(product)
            updater = create_order_window(user_type, product, int(quantity), price)
            order = submit_order(user_type, product, quantity, updater)
            result_label.config(text=f"{order.quantity} {order.product} order placed at ₦{order.price:.2f}", fg="green")
            update_matches()
            refresh_wallet_inventory()
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

if __name__ == "__main__":
    farmer_window = create_window("Farmer")
    buyer_window = create_window("Buyer")

    farmer_window.geometry("+100+100")
    buyer_window.geometry("+700+100")

    farmer_window.mainloop()
