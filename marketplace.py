import uuid
import random
from collections import deque, defaultdict

# In-memory storage
sell_orders = deque()
buy_orders = deque()
matches = []
product_stock = defaultdict(int)

wallets = {
    "Farmer": 0,
    "Buyer": random.randint(128345, 348723)  # Random starting wallet for buyer
}
inventories = {
    "Farmer": {crop: random.randint(148, 364) for crop in ["maize", "tomato", "cocoa"]}
}

active_orders = {}

base_prices = {
    "maize": 250,
    "tomato": 300,
    "cocoa": 800
}

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

def get_market_price(product):
    relevant_orders = [order for order in sell_orders if order.product == product]
    if relevant_orders:
        prices = [order.price for order in relevant_orders]
        return round(sum(prices) / len(prices), 2)
    else:
        return base_prices[product]

def match_orders():
    global sell_orders, buy_orders, matches

    new_buy_orders = deque()
    while buy_orders:
        buy = buy_orders.popleft()
        new_sell_orders = deque()

        while sell_orders:
            sell = sell_orders.popleft()
            if buy.product == sell.product:
                quantity = min(buy.remaining, sell.remaining)

                total_cost = quantity * sell.price
                if wallets["Buyer"] < total_cost:
                    new_sell_orders.appendleft(sell)
                    break

                if inventories["Farmer"][sell.product] < quantity:
                    continue

                match = Match(buy, sell, quantity, sell.price)
                matches.append(match)

                buy.remaining -= quantity
                sell.remaining -= quantity
                product_stock[sell.product] -= quantity
                inventories["Farmer"][sell.product] -= quantity

                wallets["Buyer"] -= total_cost
                wallets["Farmer"] += total_cost

                # Update active order trackers
                for order in (buy, sell):
                    if order.id in active_orders:
                        active_orders[order.id]['filled'] += quantity
                        active_orders[order.id]['callback'](active_orders[order.id]['filled'])

                if sell.remaining > 0:
                    new_sell_orders.appendleft(sell)
                if buy.remaining == 0:
                    break
            else:
                new_sell_orders.append(sell)

        sell_orders = new_sell_orders
        if buy.remaining > 0:
            new_buy_orders.append(buy)

    buy_orders = new_buy_orders

def submit_order(user_type, product, quantity, on_update_callback=None):
    quantity = int(quantity)

    if user_type == 'Farmer':
        if inventories["Farmer"][product] < quantity:
            raise Exception("Not enough inventory to sell")

    if user_type == 'Buyer':
        estimated_cost = get_market_price(product) * quantity
        if wallets["Buyer"] < estimated_cost:
            raise Exception("Insufficient funds for this order")

    order = Order(user_type, product, quantity)

    if user_type == 'Farmer':
        sell_orders.append(order)
        product_stock[product] += quantity
    else:
        buy_orders.append(order)

    if on_update_callback:
        active_orders[order.id] = {
            'filled': order.quantity - order.remaining,
            'total': order.quantity,
            'callback': lambda filled: (
                on_update_callback(filled),
                active_orders.update({
                    order.id: {
                        **active_orders[order.id],
                        'filled': filled
                    }
                })
            )
        }

    match_orders()
    return order

def get_matches():
    return [f"{m.quantity} of {m.buy_order.product} at ₦{m.price:.2f} matched" for m in matches[-10:]]

def get_current_price(product):
    return get_market_price(product)

def get_product_list():
    return list(base_prices.keys())

def get_wallet(user_type):
    return wallets[user_type]

def get_inventory():
    return inventories["Farmer"]
