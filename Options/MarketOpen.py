import os
import json
import yfinance as yf
from datetime import datetime
# import pyotp
# import robin_stocks.robinhood as r
# from dotenv import load_dotenv

def fetch_update_open_call_value():
    
    json_file_path = 'options_data.json'
    
    # Check if the JSON file exists
    if not os.path.exists(json_file_path):
        print(f"File {json_file_path} does not exist.")
        return

    # Load the existing data from the JSON file
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    # Get the last date in the data
    last_date = list(data.keys())[-1]

    for identifier, details in data[last_date].items():
        
        # Extract symbol, call price, and expiration date using regular expressions from format: "ADC $60.0 Call 2024-02-16" using regex
        symbol = identifier.split(' ')[0]
        call_price = float(identifier.split(' ')[1].replace('$', ''))
        expiration_date = identifier.split(' ')[3]

        try:
                        
            # Fetch option data from Yahoo Finance
            expiration_date = expiration_date.replace('-', '')
            
            shifted_number = int(call_price * 1000)
            formatted_number = f"{shifted_number:08d}"

            ticker_data = symbol + expiration_date[2:] + "C" + str(formatted_number)

            option = yf.Ticker(ticker_data)
            option_info = option.info
            # print("\n\n\n\n", option_info)

            midpoint = (option_info['bid'] + option_info['ask']) / 2
            print(f"mark for {symbol} {call_price} {expiration_date} is: {midpoint}")

            # Update the entry with the option's open price
            details['Option Open Price'] = round(midpoint, 2)
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")

    # Write the updated data back to the JSON file
    with open(json_file_path, 'w') as file:
        json.dump(data, file, indent=4)

    print(f"Data for {last_date} has been updated in {json_file_path}.")

def fetch_update_open_call_value_robinhood():
    # Load environment variables
    load_dotenv()

    # Generate TOTP for 2FA
    totp = pyotp.TOTP(os.environ['robin_mfa']).now()

    # Login
    login = r.login(os.environ['robin_username'],
                    os.environ['robin_password'], store_session=False, mfa_code=totp)

    json_file_path = 'options_data.json'
    
    # Check if the JSON file exists
    if not os.path.exists(json_file_path):
        print(f"File {json_file_path} does not exist.")
        return

    # Load the existing data from the JSON file
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    # Get the last date in the data
    last_date = list(data.keys())[-1]

    for identifier, details in data[last_date].items():
        
        # Extract symbol, call price, and expiration date using regular expressions from format: "ADC $60.0 Call 2024-02-16" using regex
        symbol = identifier.split(' ')[0]
        call_price = float(identifier.split(' ')[1].replace('$', ''))
        expiration_date = identifier.split(' ')[3]

        # Find options by expiration and strike
        options = r.find_options_by_expiration_and_strike(symbol, expiration_date, call_price, optionType='call')
  
        # Assuming the first option is the one we're interested in
        if options and len(options) > 0:
            option_id = options[0]['id']  # Get the option ID of the first found option
            
            # Get market data for the option
            market_data = r.get_option_market_data_by_id(option_id)
            
            # Check if market_data is not empty and access the first item
            if market_data and len(market_data) > 0:
                # print(market_data, "\n\n")
                mark_price = market_data[0].get('mark_price')

                print(f"mark for {symbol} {call_price} {expiration_date} is: {mark_price}")
            else:
                print("Could not retrieve market data for the option.")
        else:
            print("No options found matching the criteria.")

    # Write the updated data back to the JSON file
    with open(json_file_path, 'w') as file:
        json.dump(data, file, indent=4)

    print(f"Data for {last_date} has been updated in {json_file_path}.")

if __name__ == "__main__":

    # fetch_update_open_call_value_robinhood()
    fetch_update_open_call_value()