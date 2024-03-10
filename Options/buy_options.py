import robin_stocks.robinhood as r
from dotenv import load_dotenv
import pyotp
import json
import os
import time
import math

# Login using .env file
load_dotenv()
totp = pyotp.TOTP(os.environ['ROBIN_MFA']).now()
login = r.login(os.environ['ROBIN_USERNAME'],
                os.environ['ROBIN_PASSWORD'], store_session=False, mfa_code=totp)

print("Logged in")

def trade_option(symbol, strike, expirationDate, max_money_to_spend):
    # get open price for option
    options = r.find_options_by_expiration_and_strike(symbol, expirationDate, strike, optionType='call')
                
    # Get raw open price
    raw_open_price_data = r.get_option_historicals(symbol, expirationDate, strike, 'call', interval='5minute', span='day')
    open_price = float(raw_open_price_data[0]["open_price"])

    print(f"Open price: {open_price}")

    limit_price = float(open_price )* 0.90

    # round to 2 decimal places, up when needed. Ex: 0.005 -> 0.01
    limit_price = math.ceil(float(open_price) * 0.90 * 100) / 100

    # Truncate the decimals to buy always less than max amount
    quantity = int(max_money_to_spend / (limit_price*100))

    print(f"Purchasing {quantity} {symbol} {strike} Calls {expirationDate} for ${limit_price} at ${limit_price * 100 * quantity} total\n\n")

    # Place the order
    order = r.orders.order_buy_option_limit(
        positionEffect='open',
        creditOrDebit='debit',
        price=limit_price,
        symbol=symbol,
        quantity=quantity,
        expirationDate=expirationDate,
        strike=strike,
        optionType='call',  # Assuming it's a call option
        timeInForce='gfd'  # Good 'til cancelled
    )

    print(f"Order placed: {json.dumps(order, indent=4)}\n\n")

    time.sleep(1)

    # while loop to check if the order has been filled
    while True:
        # get the status of the order
        order_status = r.get_all_open_option_orders()

        # if the order has been filled, break the loop
        # print(f"Order status: {json.dumps(order_status, indent=4)}")
        if order_status == []:
            print(f"Order status: FILLED")
            break

        print(f"Pending quantity: {order_status[0]['pending_quantity']}")

        time.sleep(1)

    # print list of all current options held
    options = r.get_open_option_positions()
    print("We now own the following option:\n", json.dumps(options, indent=4))

    average_price = float(options[0]["average_price"])
    quantity = float(options[0]["quantity"])
    print(f"Average price bought: {average_price}, Quantity: {quantity}")

    sell_price = average_price * 1.4
    print(f"Selling at: {sell_price}")

    time.sleep(5)

    # sell the option with order_sell_option_limit
    order = r.orders.order_sell_option_limit(
        positionEffect='close',
        price=sell_price,
        symbol=symbol,
        quantity=quantity,
        expirationDate=expirationDate,
        strike=strike,
        optionType='call',  # Assuming it's a call option
        timeInForce='gfd'  # Good 'til cancelled
    )

    print(f"Order placed: {json.dumps(order, indent=4)}\n\n")

    # while loop to check if the order has been filled. Filled shows as options = []
    while True:
        # get the status of the order
        options = r.get_open_option_positions()

        # if the order has been filled, break the loop
        if options == []:
            print(f"Order status: SOLD")
            break

        # if the order has not been filled, wait 5 seconds and check again
        time.sleep(1)


# Buy call NVDA $950.0 Call 2024-03-15
symbol = "NVDA"
strike = 950.0
expirationDate = "2024-03-15"
max_money_to_spend = 10000

trade_option(symbol, strike, expirationDate, max_money_to_spend)