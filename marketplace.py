# marketplace.py

import uuid
from collections import deque, defaultdict

# In-memory storage
sell_orders = deque()
buy_orders = deque()
matches = []
product_stock = defaultdict(int)

# Base prices per product (₦ per unit)
base_prices = {
    "maize": 250,
    "tomato": 300,
    "cocoa": 800
}

# Order classes
class Order:
    def __init__(self, user_type, product, quantity):
        self.id = str(uuid.uuid4())
        self.user_type = user_type
        self.product = product
        self.quantity = int(quantity)
        self.price = get_market_price(product)
        self.remaining = self.quantity

class Match:
    def __init__(self, buy_order, sell_order, quantity, price):
        self.id = str(uuid.uuid4())
        self.buy_order = buy_order
        self.sell_order = sell_order
        self.quantity = quantity
        self.price = price

# Calculate dynamic market price based on stock
# More stock = lower price, less stock = higher price
# Cap the price change at ±30% from base
def get_market_price(product):
    stock = product_stock[product]
    base = base_prices[product]
    multiplier = max(0.7, min(1.3, 1.3 - 0.01 * stock))
    return round(base * multiplier, 2)

# Order matching engine
def match_orders():
    global sell_orders, buy_orders, matches

    new_buy_orders = deque()
    while buy_orders:
        buy = buy_orders.popleft()
        matched = False
        new_sell_orders = deque()

        while sell_orders:
            sell = sell_orders.popleft()
            if buy.product == sell.product:
                quantity = min(buy.remaining, sell.remaining)
                match = Match(buy, sell, quantity, sell.price)
                matches.append(match)

                buy.remaining -= quantity
                sell.remaining -= quantity
                product_stock[sell.product] -= quantity

                if sell.remaining > 0:
                    new_sell_orders.appendleft(sell)
                if buy.remaining == 0:
                    matched = True
                    break
            else:
                new_sell_orders.append(sell)

        sell_orders = new_sell_orders
        if buy.remaining > 0:
            new_buy_orders.append(buy)

    buy_orders = new_buy_orders

# Submission functions
def submit_order(user_type, product, quantity):
    order = Order(user_type, product, quantity)
    if user_type == 'Farmer':
        sell_orders.append(order)
        product_stock[product] += order.quantity
    else:
        buy_orders.append(order)
    match_orders()
    return order

def get_matches():
    return [f"{m.quantity} of {m.buy_order.product} at ₦{m.price:.2f} matched" for m in matches[-10:]]

def get_current_price(product):
    return get_market_price(product)

def get_product_list():
    return list(base_prices.keys())
