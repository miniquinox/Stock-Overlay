import os
import pyotp
import robin_stocks.robinhood as r
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Generate TOTP for 2FA
totp = pyotp.TOTP(os.environ['robin_mfa']).now()

# Login
login = r.login(os.environ['robin_username'],
                os.environ['robin_password'], store_session=False, mfa_code=totp)

# Define the option parameters
symbol = 'NVDA'  # Example: Nvidia Corporation
expirationDate = '2024-03-01'  # Format: YYYY-MM-DD
strike = '795'  # Example: $790, make sure this is a string if it's being extracted from .env or adjusted accordingly
optionType = 'call'  # 'call' or 'put'

# Find options by expiration and strike
options = r.find_options_by_expiration_and_strike(symbol, expirationDate, strike, optionType=optionType)

# Assuming the first option is the one we're interested in
if options and len(options) > 0:
    option_id = options[0]['id']  # Get the option ID of the first found option
    
    # Get market data for the option
    market_data = r.get_option_market_data_by_id(option_id)
    
    # Check if market_data is not empty and access the first item
    if market_data and len(market_data) > 0:
        # print(market_data, "\n\n")
        ask_price = market_data[0].get('mark_price')

        print(market_data, "\n")
        print(f"The mark {symbol} {strike} {expirationDate} is: {ask_price}")
    else:
        print("Could not retrieve market data for the option.")
else:
    print("No options found matching the criteria.")
