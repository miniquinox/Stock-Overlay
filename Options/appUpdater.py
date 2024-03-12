import base64
import json
import requests
import datetime
import time
import pyotp
import robin_stocks.robinhood as r
from dotenv import load_dotenv
import os
import re

# Login using Environment variables
load_dotenv()
mfa_key = os.getenv('ROBIN_MFA')
username = os.getenv('ROBIN_USERNAME')
password = os.getenv('ROBIN_PASSWORD')
if not all([mfa_key, username, password]):
    raise EnvironmentError("One or more environment variables are missing.")

# # Login using .env file
# load_dotenv()
totp = pyotp.TOTP(os.environ['ROBIN_MFA']).now()
login = r.login(os.environ['ROBIN_USERNAME'],
                os.environ['ROBIN_PASSWORD'], store_session=False, mfa_code=totp)

print("Logged in")

def get_high_option_price(symbol, exp_date, strike):
    options = r.find_options_by_expiration_and_strike(symbol, exp_date, strike, optionType='call')

    # Get option id
    option_id = options[0]['id']

    # Get market data
    market_data = r.get_option_market_data_by_id(option_id)

    # Get the high_price from the market data
    high_price = market_data[0].get('high_price')

    return high_price


def append_to_github_file(new_data):
    # Your GitHub Personal Access Token
    token = os.getenv('PERSONAL_ACCESS_TOKEN')

    # The repository and file details
    owner = "miniquinox"
    repo = "OptionsAi"
    path = "options_data_2.json"

    # The headers for the API requests
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    # Fetch the current file content
    response = requests.get(f"https://api.github.com/repos/{owner}/{repo}/contents/{path}", headers=headers)
    response.raise_for_status()  # Ensure we got a successful response

    # Decode the file content
    file_content = base64.b64decode(response.json()["content"]).decode()

    # Load the JSON data
    data = json.loads(file_content)

    # Append the new data to the existing data
    data[-1] = new_data

    # Encode the updated data
    updated_content = base64.b64encode(json.dumps(data, indent=4).encode()).decode()

    # Update the file via the API
    update_response = requests.put(
        f"https://api.github.com/repos/{owner}/{repo}/contents/{path}",
        headers=headers,
        json={
            "message": "Append new data",
            "content": updated_content,
            "sha": response.json()["sha"],  # We need to provide the current SHA of the file
        },
    )
    update_response.raise_for_status()  # Ensure we got a successful response


def check_and_update_high_price():
    # Get the personal access token from environment variables
    token = os.getenv('PERSONAL_ACCESS_TOKEN')

    # The repository and file details
    owner = "miniquinox"
    repo = "OptionsAi"
    path = "options_data_2.json"

    # The headers for the API requests
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    # Fetch the current file content
    response = requests.get(f"https://api.github.com/repos/{owner}/{repo}/contents/{path}", headers=headers)
    response.raise_for_status()  # Ensure we got a successful response

    # Decode the file content
    file_content = base64.b64decode(response.json()["content"]).decode()

    # Load the JSON data
    data = json.loads(file_content)

    date = data[-1]['date']
    new_data = {
        "date": date,
        "options": []
    }

    start_time = datetime.datetime.now()

    while True:
        
        # Check if 3 hours and 30 minutes have passed
        elapsed_time = datetime.datetime.now() - start_time
        if elapsed_time > datetime.timedelta(hours=3, minutes=30):
            break
        
        if not data[-1]['options']:
            print("Nothing to update today. Exiting...")
            break
            
        for option in data[-1]['options']:
            # Regex the option details from string format "SMCI $1040.0 Call 2024-03-08"
            option_string = option['id']

            match = re.match(r"(\w+)\s+\$(\d+\.\d+)\s+(\w+)\s+(\d{4}-\d{2}-\d{2})", option_string)

            if match:
                symbol = match.group(1)
                strike = float(match.group(2).replace(',', ''))
                option_type = match.group(3)
                exp_date = match.group(4)

                # Get raw open price
                raw_open_price_data = r.get_option_historicals(symbol, exp_date, strike, option_type, interval='5minute', span='day')
                # Convert open price to float
                open_price = float(raw_open_price_data[0]["open_price"].replace(',', ''))

                # Get high price
                high_price = float(get_high_option_price(symbol, exp_date, strike).replace(',', ''))

                if high_price > open_price:
                    percentage = round((high_price - open_price) / open_price * 100, 2)
                    if percentage > option['percentage']:
                        option['percentage'] = percentage
                        print(f"Updating high price for {symbol} {strike} {exp_date} to {high_price} with a percentage of {percentage}%")
                        new_data['options'].append(option)
                    else:
                        print(f"No update for {symbol} {strike} {exp_date} as the high price is {high_price} and the open price is {open_price}")
                else:
                    new_data['options'].append(option)

        if new_data['options']:
            append_to_github_file(new_data)
            new_data['options'] = []

        # Wait for a minute before the next check
        time.sleep(10)

# Usage:
check_and_update_high_price()