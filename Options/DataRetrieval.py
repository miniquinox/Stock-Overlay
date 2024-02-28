import os
import json
import pyotp
import robin_stocks.robinhood as r
from dotenv import load_dotenv

def fetch_update_max_call_value():
    
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

    # if key has empty value, skip
    if not data[last_date]:
        print(f"Data for {last_date} is empty. Nothing to report today.")
        return
    
    # Login using Environment variables
    load_dotenv()
    mfa_key = os.getenv('ROBIN_MFA')
    username = os.getenv('ROBIN_USERNAME')
    password = os.getenv('ROBIN_PASSWORD')
    if not all([mfa_key, username, password]):
        raise EnvironmentError("One or more environment variables are missing.")

    # # Login using .env file
    # load_dotenv()
    # totp = pyotp.TOTP(os.environ['ROBIN_MFA']).now()
    # login = r.login(os.environ['ROBIN_USERNAME'],
    #                 os.environ['ROBIN_PASSWORD'], store_session=False, mfa_code=totp)
    
    
    print("Logged in")


    json_file_path = 'options_data.json'

    for identifier, details in data[last_date].items():
        
        # Extract symbol, call price, and expiration date using regular expressions from format: "ADC $60.0 Call 2024-02-16" using regex
        symbol = identifier.split(' ')[0]
        call_price = float(identifier.split(' ')[1].replace('$', ''))
        expiration_date = identifier.split(' ')[3]

        try:
            # Find options by expiration and strike
            options = r.find_options_by_expiration_and_strike(symbol, expiration_date, call_price, optionType='call')
            
            # Get raw open price
            raw_open_price_data = r.get_option_historicals(symbol, expiration_date, call_price, 'call', interval='5minute', span='day')
            
            # Convert open price to float
            open_price = float(raw_open_price_data[0]["open_price"])

            # Get option id
            option_id = options[0]['id']

            # Get market data
            market_data = r.get_option_market_data_by_id(option_id)

            # Convert max price to float
            max_price = float(market_data[0].get('high_price'))

            # Get max 24h value
            historical_data = r.get_stock_historicals(symbol, span='day', bounds='regular')      
            max_24h_value = max([float(data['high_price']) for data in historical_data])

            # Store details
            details['Max Day Stock Price'] = round(max_24h_value, 2)
            details['Option Open Price'] = open_price
            details['Max Day Call Price'] = max_price

            print(f"Updated data for {symbol} with Max Day Stock Price: {max_24h_value}, Option Open Price: {open_price}, and Max Day Call Price: {max_price}.")
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
    
    # Write the updated data back to the JSON file
    with open(json_file_path, 'w') as file:
        json.dump(data, file, indent=4)

    print(f"Data for {last_date} has been updated in {json_file_path}.")
    
    options_data = data[last_date]

    # Prepare the content to be appended to the README
    content_to_append = f"### {last_date}\n\n"
    content_to_append += "| Option ID | Performance |\n"
    content_to_append += "| --- | --- |\n"

    # if key has empty value, skip
    if not data[last_date]:
        content_to_append += f"| No good options today | Nothing to report |\n"

    for option_id, details in options_data.items():
        open_price = details["Option Open Price"]
        max_price = details["Max Day Call Price"]
        
        # Calculate performance
        if open_price > 0:  # Avoid division by zero
            performance = ((max_price - open_price) / open_price) * 100
            if performance < 40:
                performance_str = f"🔴 {performance:.2f}% (DID NOT REACH 40%. Consider -20%)"
            else:
                performance_str = f"🟢 {performance:.2f}%"
        else:
            performance_str = "N/A"

        content_to_append += f"| {option_id} | Open @ {open_price} -> Max @ {max_price} = {performance_str} |\n"

    # Read the existing lines
    with open('ReadMe.md', 'r') as readme_file:
        lines = readme_file.readlines()

    # Insert the new content after the second line
    lines.insert(2, content_to_append + "\n")

    # Write the lines back to the file
    with open('ReadMe.md', 'w') as readme_file:
        readme_file.writelines(lines)

    print("Appended new data to ReadMe.md.")

if __name__ == "__main__":
    
    fetch_update_max_call_value()
