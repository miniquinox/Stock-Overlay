import yfinance as yf
import re
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import base64
import json
import requests
import sys
import os
import robin_stocks.robinhood as r
from dotenv import load_dotenv
import pyotp
import asyncio
from telegram import Bot
import datetime
from datetime import datetime as dt

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
    data.append(new_data)

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

def track_market_data(test_symbol, test_expiration, test_strike, duration=2400, sleep_interval=5):
    start_time = datetime.datetime.now()

    while True:
        current_time = datetime.datetime.now()
        elapsed_time = (current_time - start_time).total_seconds()

        # Check if duration seconds have passed
        if elapsed_time > duration:
            break

        # Your code to fetch market data and print information
        current_market_price = r.get_option_market_data(test_symbol, test_expiration, test_strike, optionType='call')
        my_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        my_loop = ""
        my_loop += f"Time: {my_time}\n"
        my_loop += f"{test_symbol} Last Trade Price {current_market_price[0][0]['last_trade_price']} \n"
        my_loop += f"{test_symbol} Ask Price {current_market_price[0][0]['ask_price']} \n"
        my_loop += f"{test_symbol} Bid Price {current_market_price[0][0]['bid_price']} \n"
        my_loop += f"{test_symbol} Mark Price {current_market_price[0][0]['mark_price']} \n"
        
        # Get raw open price
        raw_open_price_data = r.get_option_historicals(test_symbol, test_expiration, test_strike, 'call', interval='5minute', span='day')
        open_price = float(raw_open_price_data[0]["open_price"])
        my_loop += f"{test_symbol} Open Price {open_price} \n"
        
        print(my_loop)

        time.sleep(sleep_interval)  # Sleep for sleep_interval seconds before the next iteration

        with open("time_tracking.txt", "a") as file:
            file.write(f"{my_loop} \n")

async def send_telegram_options(options_data):
    bot_token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('CHAT_ID')
    bot = Bot(token=bot_token)

    # Using await to call the coroutine send_message
    await bot.send_message(chat_id=chat_id, text=options_data)

async def send_telegram_time_tracking():
    bot_token = os.getenv('TELEGRAM_TOKEN')
    chat_id_test = os.getenv('CHAT_ID_TEST')
    bot = Bot(token=bot_token)

    # Using await to call the coroutine send_message
    await bot.send_document(chat_id=chat_id_test, document=open('time_tracking.txt', 'rb'))

def fetch_and_calculate_option_price():
    
    # Web scraping with Selenium
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') # Important for running in a headless environment
    options.add_argument('--no-sandbox') # Bypass OS security model, required for running in containers
    options.add_argument('--disable-dev-shm-usage') # Overcome limited resource problems
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    driver.get(f'https://stockanalysis.com/stocks/screener/')
    wait = WebDriverWait(driver, 10)
    print("Page loaded")
    time.sleep(2)

    # Click on "Add Filters" button
    button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Add Filters')]/ancestor::button")))
    button.click()
    time.sleep(0.5)

    # Click on checkbox "Market Cap"
    marketCap = wait.until(EC.element_to_be_clickable((By.ID, "marketCap")))
    marketCap.click()
    time.sleep(0.5)
    
    # Click on checkbox "Premarket % Change"
    postmarketChangePercent = wait.until(EC.element_to_be_clickable((By.ID, "premarketChangePercent")))
    postmarketChangePercent.click()
    time.sleep(0.5)

    # Click on "Premarket Price"
    afterHoursPrice = wait.until(EC.element_to_be_clickable((By.ID, "premarketPrice")))
    afterHoursPrice.click()
    time.sleep(0.5)

    # Click on "Previous Close"
    marketClosePrice = wait.until(EC.element_to_be_clickable((By.ID, "close")))
    marketClosePrice.click()
    time.sleep(0.5)

    # Click on Close button
    close_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Close"]')))
    close_button.click()
    time.sleep(0.5)
    print("Filters added")

    # Click the first dropdown for "Market Cap"
    first_any_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Any']]")))
    first_any_button.click()
    time.sleep(0.5)

    input_element = driver.find_element(By.CSS_SELECTOR, "input[placeholder='Value']")
    input_element.clear()  # Clear any pre-existing text in the input field
    input_element.send_keys("2B")
    time.sleep(0.5)
    
    # Click the second dropdown for "After-Hours % Change"
    second_any_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Any']]")))
    second_any_button.click()
    time.sleep(0.5)

    input_element = driver.find_element(By.CSS_SELECTOR, "input[placeholder='Value']")
    input_element.clear()  # Clear any pre-existing text in the input field
    input_element.send_keys("10")
    print("Filters set")
    
    time.sleep(0.5)

    # Click button with text "Filters"
    button_xpath = "//li/button[contains(@class, 'dont-move') and contains(text(), 'Filters')]"
    filters_button = wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
    filters_button.click()
    time.sleep(2)

    # Get text from tbody
    tbody = driver.find_element(By.CSS_SELECTOR, 'tbody')

    # Parse the text into a dic
    column_names = ['Symbol', 'Company Name', 'Market Cap', 'Premkt. Chg.', 'Premkt. Price', 'Close']

    # Initialize an empty list to hold the dictionaries
    data = []

    # Split the text by lines
    lines = tbody.text.strip().split('\n')

    # Process each line with regex
    for line in lines:
        # Regex to match the structure of each line, considering complex company names
        match = re.match(r'(\w+)\s+([\w\s,.&-]+?)\s+(\d+\.\d+B)\s+(-?\d+\.\d+%)?\s+([\d,.]+)\s+(-|[\d,.]+)', line)

        if match:
            fields = match.groups()
            # Adjust for complex company names by capturing additional detail in the regex
            row_dict = {column_names[i]: fields[i] for i in range(len(column_names))}
            data.append(row_dict)

        
    # Print the list of dictionaries
    json_data = json.dumps(data, indent=4)

    # Browser is not needed anymore
    driver.quit()
    print("Browser closed")

    # Loop over the list of dictionaries and print each one
    json_data = json.loads(json_data)

    # Define the path to the JSON file
    json_file_path = 'options_data.json'

    # Initialize or load the existing data
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as file:
            try:
                results = json.load(file)
            except json.JSONDecodeError:
                results = {}
    else:
        results = {}

    # Today's date as a string
    today_str = dt.today().strftime('%Y-%m-%d')
    
    # Ensure the entry for today's date exists in the results dictionary
    if today_str not in results:
        results[today_str] = {}  # Initialize an empty dictionary for today if it doesn't exist

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

    telegram = "Today's options picks:\n"

    # Prepare the new data
    new_data = {
        "date": today_str,
        "options": []
    }

    for row in json_data:
        symbol = row["Symbol"]
        preMarketPrice = row["Premkt. Price"]
        marketClosePrice = row["Close"]
        
        # Fetch option data from Yahoo Finance.
        stock = yf.Ticker(symbol)

        if len(stock.options) == 0:
            continue
        
        options = stock.option_chain(stock.options[0])
        calls = options.calls

        # Find call with target price closest to postMarketPrice
        call_option = calls.iloc[(calls['strike'] - float(preMarketPrice.replace(',', ''))).abs().argsort()[:1]]        
        # print(call_option)
        target_strike = call_option['strike'].iloc[0]
        
        # Extract symbol, strike price, and expiration date using regular expressions
        target_expiration = dt.strptime(stock.options[0], '%Y-%m-%d').strftime('%Y-%m-%d')
        
        # Convert target_expiration to a datetime object
        target_expiration_date = dt.strptime(target_expiration, '%Y-%m-%d')

        # Get today's date
        today = dt.today()

        # Calculate the difference in days
        difference = (target_expiration_date - today).days

        # If the difference is more than 8 days, skip this option
        if difference > 6:
            continue


        try:
            stock_close_price = r.get_stock_quote_by_symbol(symbol)['previous_close']
            current_stock_price = r.get_latest_price(symbol)[0]
            options = r.find_options_by_expiration_and_strike(symbol, target_expiration, target_strike, optionType='call')
            option_market_close = options[0]["previous_close_price"] 

        except:
            print(f"Error fetching data for {symbol}")
            continue

        print(f'\n\nStock price at market close: {stock_close_price} for {symbol}')
        print(f'Stock price before market open: {current_stock_price} for {symbol}')
        print(f'Option price at market close: {option_market_close} for {symbol}')

        results[today_str][f"{symbol} ${target_strike} Call {target_expiration}"] = {
            "Stock price at market close": float(stock_close_price.replace(',', '')),
            "Stock price before market open": float(current_stock_price.replace(',', '')),
            "Option price at market close": float(option_market_close.replace(',', ''))
        }

        option_telegram = f'    {symbol} ${target_strike} Call {target_expiration}\n'
        telegram += option_telegram

        option_id = f"{symbol} ${target_strike} Call {target_expiration}"
        
        test_symbol = symbol
        test_strike = target_strike
        test_expiration = target_expiration

        # Append to the new data
        new_data["options"].append({
            "id": option_id,
            "percentage": 0
        })
    
    append_to_github_file(new_data)

    # After updating results with today's data, write the updated dictionary back to the file        
    with open(json_file_path, 'w') as file:
        json.dump(results, file, indent=4)

    print(f"Data for {today_str} has been added to {json_file_path}.")

    asyncio.run(send_telegram_options(telegram))

    # Track market data for 40 minutes
    track_market_data(test_symbol, test_expiration, test_strike, duration=400, sleep_interval=5)

    asyncio.run(send_telegram_time_tracking())
        

if __name__ == "__main__":
    fetch_and_calculate_option_price()
    sys.exit(0)  # Exit successfully
