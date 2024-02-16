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

def fetch_and_calculate_option_price(input_format):
    """
    Fetch and calculate the option price given an input in the format 'TTD $90 Call 2/16'.
    """
    # Extract symbol, strike price, and expiration date using regular expressions
    match = re.match(r'(\w+)\s+\$(\d+)\s+(\w+)\s+(\d+/\d+)', input_format)
    symbol, target_strike, _, target_expiration = match.groups()
    target_strike = int(target_strike)
    target_expiration = datetime.strptime(target_expiration, '%m/%d').replace(year=datetime.now().year).strftime('%Y-%m-%d')
    
    # Fetch option data from Yahoo Finance
    stock = yf.Ticker(symbol)
    options = stock.option_chain(target_expiration)
    calls = options.calls
    
    call_option = calls.iloc[(calls['strike'] - target_strike).abs().argsort()[:1]]
    if call_option.empty:
        return "No options found for the given strike price and expiration date"
    
    implied_volatility = call_option['impliedVolatility'].iloc[0] * 100
    ask_price = call_option['ask'].iloc[0]
    current_price = stock.info['currentPrice']
    
    # Calculate the Greeks
    interest_rate = 1
    days_to_expiration = max((datetime.strptime(target_expiration, '%Y-%m-%d') - datetime.now()).days / 365, 1/365)
    bs = mibian.BS([current_price, target_strike, interest_rate, days_to_expiration], volatility=implied_volatility)
    
    # Web scraping with Selenium
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    driver.get(f'https://finance.yahoo.com/quote/{symbol}')
    time.sleep(2)
    postMarketPrice = driver.find_element(By.CSS_SELECTOR, f'fin-streamer[data-field="postMarketPrice"][data-symbol="{symbol}"]').text
    regularMarketPrice = driver.find_element(By.CSS_SELECTOR, f'fin-streamer[data-field="regularMarketPrice"][data-symbol="{symbol}"]').text
    driver.quit()
    
    S = float(postMarketPrice)
    K = target_strike
    T = days_to_expiration
    r = 0.01
    sigma = implied_volatility / 100
    estimate = (S * norm.cdf((np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))) - 
                K * np.exp(-r * T) * norm.cdf((np.log(S / K) + (r - 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))))
    
    print(f"\n{input_format}")
    print(f'The stock value of {symbol} at market close is ${regularMarketPrice}')
    print(f"The after hours stock value of {symbol} is ${postMarketPrice}")
    print(f"Call Option Price at market close: ${ask_price}")
    print(f"Call Option Price (expected) after market opens: ${estimate:.2f}\n")

# Example usage
input_format = "COIN $185 Call 2/16"  # Replace this with actual user input
# input_format = input("Enter the option in the format 'TTD $90 Call 2/16': ")
fetch_and_calculate_option_price(input_format)
