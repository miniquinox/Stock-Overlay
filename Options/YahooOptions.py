import yfinance as yf
import mibian
from datetime import datetime
import re
import numpy as np
from scipy.stats import norm
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import json
import sys
import os

def fetch_and_calculate_option_price():
    """
    Fetch and calculate the option price given an input in the format 'TTD $90 Call 2/16'.
    """
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
    input_element.send_keys("12")
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
    today_str = datetime.today().strftime('%Y-%m-%d')
    
    # Ensure the entry for today's date exists in the results dictionary
    if today_str not in results:
        results[today_str] = {}  # Initialize an empty dictionary for today if it doesn't exist

    for row in json_data:
        symbol = row["Symbol"]
        postMarketPrice = row["Premkt. Price"]
        marketClosePrice = row["Close"]
        
        # Fetch option data from Yahoo Finance
        stock = yf.Ticker(symbol)

        # Sometimes, the options attribute is empty. In that case, skip the current symbol
        if len(stock.options) == 0:
            continue

        options = stock.option_chain(stock.options[0])
        calls = options.calls

        # Find call with target price closest to postMarketPrice
        call_option = calls.iloc[(calls['strike'] - float(postMarketPrice)).abs().argsort()[:1]]
        
        # print(call_option)
        target_strike = call_option['strike'].iloc[0]
        
        # Extract symbol, strike price, and expiration date using regular expressions
        target_expiration = datetime.strptime(stock.options[0], '%Y-%m-%d').strftime('%Y-%m-%d')
        
        # Convert target_expiration to a datetime object
        target_expiration_date = datetime.strptime(target_expiration, '%Y-%m-%d')

        # Get today's date
        today = datetime.today()

        # Calculate the difference in days
        difference = (target_expiration_date - today).days

        # If the difference is more than 8 days, skip this option
        if difference > 8:
            continue

        implied_volatility = call_option['impliedVolatility'].iloc[0] * 100

        id = call_option['contractSymbol'].iloc[0]
        ask_price = yf.Ticker(id).info['previousClose']

        current_price = stock.info['currentPrice']
        
        # Calculate the Greeks
        interest_rate = 1
        days_to_expiration = max((datetime.strptime(target_expiration, '%Y-%m-%d') - datetime.now()).days / 365, 1/365)
        bs = mibian.BS([current_price, target_strike, interest_rate, days_to_expiration], volatility=implied_volatility)

        S = float(postMarketPrice)
        K = target_strike
        T = days_to_expiration
        r = 0.01
        sigma = implied_volatility / 100
        estimate = (S * norm.cdf((np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))) - 
                    K * np.exp(-r * T) * norm.cdf((np.log(S / K) + (r - 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))))
        
        results[today_str][f"{symbol} ${target_strike} Call {target_expiration}"] = {
            "Stock price at market close": float(marketClosePrice),
            "Stock price before market open": float(marketClosePrice),
            "Option price at market close": float(ask_price),
            "Predicted option price at market open": float(f'{estimate:.2f}')
        }
        
        # Print Call id as "AMAT $210 Call 2/16" format
        print(f"\n{symbol} ${target_strike} Call {target_expiration}")
        print(f'Stock price at market-close:         ${marketClosePrice}')
        print(f"Stock price at pre-market open:      ${postMarketPrice}")
        print(f"Call price at market-close:          ${ask_price}")
        print(f"Expected call price market-open:     ${estimate:.2f}")
        print(f'Change in % after hours:             {round((float(postMarketPrice) - float(marketClosePrice)) / float(marketClosePrice) * 100, 2)}%\n')
    
    # After updating results with today's data, write the updated dictionary back to the file
    with open(json_file_path, 'w') as file:
        json.dump(results, file, indent=4)

    print(f"Data for {today_str} has been added to {json_file_path}.")

if __name__ == "__main__":
    fetch_and_calculate_option_price()
    sys.exit(0)  # Exit successfully
