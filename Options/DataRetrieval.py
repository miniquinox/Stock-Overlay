import os
import json
import yfinance as yf
from datetime import datetime

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

    for identifier, details in data[last_date].items():
        
        # Extract symbol, call price, and expiration date using regular expressions from format: "ADC $60.0 Call 2024-02-16" using regex
        symbol = identifier.split(' ')[0]
        call_price = float(identifier.split(' ')[1].replace('$', ''))
        expiration_date = identifier.split(' ')[3]

        try:
            # Fetch data from Yahoo Finance
            stock = yf.Ticker(symbol)
            
            # Fetch the max stock value from previous day
            hist = stock.history(period='1d')
            # print("\n\n\n\n", hist)
            
            max_24h_value = hist['High'].iloc[0]

            # Fetch option data from Yahoo Finance
            expiration_date = expiration_date.replace('-', '')
            
            shifted_number = int(call_price * 1000)
            formatted_number = f"{shifted_number:08d}"

            ticker_data = symbol + expiration_date[2:] + "C" + str(formatted_number)

            option = yf.Ticker(ticker_data)
            option_info = option.info

            # Update the entry with the max 24h call value
            details['Max Day Stock Price'] = round(max_24h_value, 2)
            details['Max Day Call Price'] = round(option_info['dayHigh'], 2)
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")

    # Write the updated data back to the JSON file
    with open(json_file_path, 'w') as file:
        json.dump(data, file, indent=4)

    print(f"Data for {last_date} has been updated in {json_file_path}.")

def DailyPerformance():
    # Load JSON data
    with open('options_data.json', 'r') as file:
        data = json.load(file)

    # Get the last date from the JSON data
    last_date = sorted(data.keys())[-1]
    
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
            if performance < 50:
                performance_str = f"🔴 {performance:.2f}% (DID NOT REACH 50%. Consider -20%)"
            else:
                performance_str = f"🟢 {performance:.2f}%"
        else:
            performance_str = "N/A"

        content_to_append += f"| {option_id} | Open @ {open_price} -> Max @ {max_price} = {performance_str} |\n"

    # Append the content to the README file
    with open('README.md', 'a') as readme_file:
        readme_file.write(content_to_append + "\n")

    print("Appended new data to README.md.")

if __name__ == "__main__":
    
    fetch_update_max_call_value()
    DailyPerformance()