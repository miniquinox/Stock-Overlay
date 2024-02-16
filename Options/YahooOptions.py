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

def fetch_and_calculate_option_price():
    """
    Fetch and calculate the option price given an input in the format 'TTD $90 Call 2/16'.
    """
    # Web scraping with Selenium
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    driver.get(f'https://stockanalysis.com/stocks/screener/')
    wait = WebDriverWait(driver, 10)
    print("Page loaded")
    time.sleep(2)

    # Click on "Add Filters" button
    button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Add Filters')]/ancestor::button")))
    button.click()
    time.sleep(1)

    # Click on checkbox "After-Hours % Change"
    postmarketChangePercent = wait.until(EC.element_to_be_clickable((By.ID, "postmarketChangePercent")))
    postmarketChangePercent.click()
    time.sleep(1)

    # Click on checkbox "Market Cap"
    marketCap = wait.until(EC.element_to_be_clickable((By.ID, "marketCap")))
    marketCap.click()
    time.sleep(1)

    # Click on After-Hours Price
    afterHoursPrice = wait.until(EC.element_to_be_clickable((By.ID, "postmarketPrice")))
    afterHoursPrice.click()
    time.sleep(1)

    # Click on Regular Market Price
    regularMarketPrice = wait.until(EC.element_to_be_clickable((By.ID, "price")))
    regularMarketPrice.click()
    time.sleep(1)

    # Click on Close button
    close_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Close"]')))
    close_button.click()
    time.sleep(1)
    print("Filters added")

    # Click the first dropdown for "After-Hours % Change"
    first_any_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Any']]")))
    first_any_button.click()
    time.sleep(1)

    input_element = driver.find_element(By.CSS_SELECTOR, "input[placeholder='Value']")
    input_element.clear()  # Clear any pre-existing text in the input field
    input_element.send_keys("15")
    time.sleep(1)
    
    # Click the second dropdown for "Market Cap"
    second_any_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Any']]")))
    second_any_button.click()
    time.sleep(1)

    input_element = driver.find_element(By.CSS_SELECTOR, "input[placeholder='Value']")
    input_element.clear()  # Clear any pre-existing text in the input field
    input_element.send_keys("2B")
    print("Filters set")
    
    time.sleep(1)

    # Click button with text "Filters"
    button_xpath = "//li/button[contains(@class, 'dont-move') and contains(text(), 'Filters')]"
    filters_button = wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
    filters_button.click()
    time.sleep(1)

    # Get text from tbody
    tbody = driver.find_element(By.CSS_SELECTOR, 'tbody')
    # print(tbody.text)

    # Parse the text into a dic
    column_names = ['Symbol', 'Company Name', 'Afterhr. Chg%', 'Market Cap', 'Afterhr. Price', 'Stock Price']

    # Initialize an empty list to hold the dictionaries
    data = []

    # Split the text by lines
    lines = tbody.text.strip().split('\n')

    # Process each line with regex
    for line in lines:
        # Regex to match the structure of each line, considering complex company names
        match = re.match(r'(\w+)\s+(.+?)\s+(-?\d+\.\d+%)\s+([\d.]+[BM])\s+([\d.]+)\s+([\d.]+)', line)
        if match:
            fields = match.groups()
            # Adjust for complex company names by capturing additional detail in the regex
            row_dict = {column_names[i]: fields[i] for i in range(len(column_names))}
            data.append(row_dict)

        
    # Print the list of dictionaries
    json_data = json.dumps(data, indent=4)
    # print(json_data)

    foo_data = [
        {
            "Symbol": "AMAT",
            "Company Name": "Applied Materials",
            "Afterhr. Chg%": "12.01%",
            "Market Cap": "156.14B",
            "Afterhr. Price": "210.20",
            "Stock Price": "187.66"
        },
        {
            "Symbol": "COIN",
            "Company Name": "Coinbase Global",
            "Afterhr. Chg%": "14.30%",
            "Market Cap": "39.64B",
            "Afterhr. Price": "189.36",
            "Stock Price": "165.67"
        },
        {
            "Symbol": "TTD",
            "Company Name": "The Trade Desk",
            "Afterhr. Chg%": "19.51%",
            "Market Cap": "37.12B",
            "Afterhr. Price": "90.48",
            "Stock Price": "75.71"
        },
        {
            "Symbol": "PCOR",
            "Company Name": "Procore Technologies",
            "Afterhr. Chg%": "9.39%",
            "Market Cap": "10.70B",
            "Afterhr. Price": "81.59",
            "Stock Price": "74.59"
        },
        {
            "Symbol": "TOST",
            "Company Name": "Toast",
            "Afterhr. Chg%": "5.99%",
            "Market Cap": "10.36B",
            "Afterhr. Price": "20.35",
            "Stock Price": "19.20"
        },
        {
            "Symbol": "BIO",
            "Company Name": "Bio-Rad Laboratories",
            "Afterhr. Chg%": "6.50%",
            "Market Cap": "9.58B",
            "Afterhr. Price": "350.10",
            "Stock Price": "328.73"
        },
        {
            "Symbol": "TXRH",
            "Company Name": "Texas Roadhouse",
            "Afterhr. Chg%": "6.06%",
            "Market Cap": "8.94B",
            "Afterhr. Price": "142.00",
            "Stock Price": "133.89"
        },
        {
            "Symbol": "MUSA",
            "Company Name": "Murphy USA",
            "Afterhr. Chg%": "5.03%",
            "Market Cap": "8.35B",
            "Afterhr. Price": "412.39",
            "Stock Price": "392.66"
        },
        {
            "Symbol": "ACHC",
            "Company Name": "Acadia Healthcare Company",
            "Afterhr. Chg%": "5.00%",
            "Market Cap": "7.67B",
            "Afterhr. Price": "87.36",
            "Stock Price": "83.20"
        },
        {
            "Symbol": "UGP",
            "Company Name": "Ultrapar Participa\u00e7\u00f5es",
            "Afterhr. Chg%": "5.91%",
            "Market Cap": "6.43B",
            "Afterhr. Price": "6.27",
            "Stock Price": "5.92"
        },
        {
            "Symbol": "BPMC",
            "Company Name": "Blueprint Medicines",
            "Afterhr. Chg%": "5.06%",
            "Market Cap": "5.32B",
            "Afterhr. Price": "92.00",
            "Stock Price": "87.57"
        },
        {
            "Symbol": "HASI",
            "Company Name": "Hannon Armstrong Sustainable Infrastructure Capital",
            "Afterhr. Chg%": "6.35%",
            "Market Cap": "2.84B",
            "Afterhr. Price": "27.14",
            "Stock Price": "25.52"
        },
        {
            "Symbol": "CORT",
            "Company Name": "Corcept Therapeutics",
            "Afterhr. Chg%": "6.30%",
            "Market Cap": "2.52B",
            "Afterhr. Price": "26.00",
            "Stock Price": "24.46"
        }
    ]
    
    
    # time.sleep(1000)

    # Loop over the list of dictionaries and print each one
    json_data = json.loads(json_data)
    for row in json_data:
        symbol = row["Symbol"]
        postMarketPrice = row["Afterhr. Price"]
        regularMarketPrice = row["Stock Price"]
        
        # Fetch option data from Yahoo Finance
        stock = yf.Ticker(symbol)

        options = stock.option_chain(stock.options[0])
        calls = options.calls

        # Find call with target price closest to postMarketPrice
        call_option = calls.iloc[(calls['strike'] - float(postMarketPrice)).abs().argsort()[:1]]
        
        # print(call_option)
        target_strike = call_option['strike'].iloc[0]
        
        # Extract symbol, strike price, and expiration date using regular expressions
        target_expiration = datetime.strptime(stock.options[0], '%Y-%m-%d').strftime('%Y-%m-%d')
        
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
        
        # Print Call id as "AMAT $210 Call 2/16" format
        print(f"{symbol} ${target_strike} Call {target_expiration}")
        print(f'The stock value of {symbol} at market close is ${regularMarketPrice}')
        print(f"The after hours stock value of {symbol} is ${postMarketPrice}")
        print(f"Call Option Price at market close: ${ask_price}")
        print(f"Call Option Price (expected) after market opens: ${estimate:.2f}\n")

# Example usage
fetch_and_calculate_option_price()
