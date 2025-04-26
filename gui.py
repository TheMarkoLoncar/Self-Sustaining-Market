import tkinter as tk
from tkinter import ttk, messagebox
import marketplace

root = tk.Tk()
root.title("Crop Marketplace")
root.geometry("800x600")

order_windows = []

# === UI Components ===

# Wallet and Inventory Display
wallet_label = tk.Label(root, text="", font=("Arial", 12))
wallet_label.pack(pady=10)

inventory_label = tk.Label(root, text="", font=("Arial", 12))
inventory_label.pack(pady=5)

# Crop Price Frame
price_frame = tk.Frame(root)
price_frame.pack(pady=10)
price_labels = {}

# Tabs
tab_control = ttk.Notebook(root)
farmer_tab = ttk.Frame(tab_control)
buyer_tab = ttk.Frame(tab_control)
tab_control.add(farmer_tab, text="Farmer")
tab_control.add(buyer_tab, text="Buyer")
tab_control.pack(expand=1, fill="both")

# Match Display
match_list = tk.Listbox(root, height=10, width=80)
match_list.pack(pady=10)

# === Functions ===

def refresh_wallet_inventory():
    wallet_label.config(text=f"Farmer Wallet: ₦{marketplace.get_wallet('Farmer'):,} | Buyer Wallet: ₦{marketplace.get_wallet('Buyer'):,}")
    inv = marketplace.get_inventory()
    inventory_label.config(text="Farmer Inventory: " + ", ".join([f"{k}: {v}kg" for k, v in inv.items()]))

def refresh_prices():
    for product in marketplace.get_product_list():
        price = marketplace.get_current_price(product)
        if product in price_labels:
            price_labels[product].config(text=f"{product.capitalize()}: ₦{price:.2f}")

def refresh_matches():
    match_list.delete(0, tk.END)
    for match in marketplace.get_matches():
        match_list.insert(tk.END, match)

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

        refresh_wallet_inventory()

    order_windows.append(win)
    return update_progress

def submit_order(user_type, product_entry, quantity_entry):
    try:
        product = product_entry.get()
        quantity = int(quantity_entry.get())
        update_cb = create_order_window(user_type, product, quantity, marketplace.get_current_price(product))
        marketplace.submit_order(user_type, product, quantity, update_cb)
        refresh_prices()
        refresh_matches()
        refresh_wallet_inventory()
    except Exception as e:
        messagebox.showerror("Error", str(e))

# === Farmer Tab ===

tk.Label(farmer_tab, text="Select Crop:").pack(pady=5)
farmer_product_entry = ttk.Combobox(farmer_tab, values=marketplace.get_product_list())
farmer_product_entry.pack(pady=5)
farmer_product_entry.set(marketplace.get_product_list()[0])

tk.Label(farmer_tab, text="Quantity to Sell (kg):").pack(pady=5)
farmer_quantity_entry = tk.Entry(farmer_tab)
farmer_quantity_entry.pack(pady=5)

tk.Button(farmer_tab, text="Submit Sell Order",
          command=lambda: submit_order("Farmer", farmer_product_entry, farmer_quantity_entry)).pack(pady=10)

# === Buyer Tab ===

tk.Label(buyer_tab, text="Select Crop:").pack(pady=5)
buyer_product_entry = ttk.Combobox(buyer_tab, values=marketplace.get_product_list())
buyer_product_entry.pack(pady=5)
buyer_product_entry.set(marketplace.get_product_list()[0])

tk.Label(buyer_tab, text="Quantity to Buy (kg):").pack(pady=5)
buyer_quantity_entry = tk.Entry(buyer_tab)
buyer_quantity_entry.pack(pady=5)

tk.Button(buyer_tab, text="Submit Buy Order",
          command=lambda: submit_order("Buyer", buyer_product_entry, buyer_quantity_entry)).pack(pady=10)

# === Crop Prices Display ===

tk.Label(price_frame, text="Current Crop Prices:", font=("Arial", 12, "bold")).pack()
for crop in marketplace.get_product_list():
    lbl = tk.Label(price_frame, text="", font=("Arial", 11))
    lbl.pack()
    price_labels[crop] = lbl

# === Initial Refresh ===

refresh_wallet_inventory()
refresh_prices()
refresh_matches()

# === Run ===

root.mainloop()
