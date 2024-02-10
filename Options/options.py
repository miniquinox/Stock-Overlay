import pandas as pd
import numpy as np
import yfinance as yf
import datetime

def options_chain(symbol):

    tk = yf.Ticker(symbol)
    # Expiration dates
    exps = tk.options

    # Get options for each expiration
    options_list = []
    for e in exps:
        opt = tk.option_chain(e)
        calls = opt.calls
        puts = opt.puts
        calls['expirationDate'] = e
        puts['expirationDate'] = e
        options_list.append(calls)
        options_list.append(puts)

    options = pd.concat(options_list, ignore_index=True)

    # Bizarre error in yfinance that gives the wrong expiration date
    # Add 1 day to get the correct expiration date
    options['expirationDate'] = pd.to_datetime(options['expirationDate']) + datetime.timedelta(days = 1)
    options['dte'] = (options['expirationDate'] - datetime.datetime.today()).dt.days / 365
    
    # Boolean column if the option is a CALL
    options['CALL'] = options['contractSymbol'].str[4:].apply(
        lambda x: "C" in x)
    
    options[['bid', 'ask', 'strike']] = options[['bid', 'ask', 'strike']].apply(pd.to_numeric)
    options['mark'] = (options['bid'] + options['ask']) / 2 # Calculate the midpoint of the bid-ask
    
    # Drop unnecessary and meaningless columns
    options = options.drop(columns = ['contractSize', 'currency', 'change', 'percentChange', 'lastTradeDate', 'lastPrice'])

    return options

# Example
symbol = 'AAPL'
options = options_chain(symbol)
print(options)


def my_options_chain(symbol, specific_contract=None):
    tk = yf.Ticker(symbol)
    # Expiration dates
    exps = tk.options

    # Get options for each expiration
    options_list = []
    for e in exps:
        opt = tk.option_chain(e)
        calls = opt.calls
        puts = opt.puts
        calls['expirationDate'] = e
        puts['expirationDate'] = e
        options_list.append(calls)
        options_list.append(puts)

    options = pd.concat(options_list, ignore_index=True)

    # Fix the expiration date
    options['expirationDate'] = pd.to_datetime(options['expirationDate']) + datetime.timedelta(days=1)
    options['dte'] = (options['expirationDate'] - datetime.datetime.today()).dt.days / 365
    
    # Boolean column if the option is a CALL
    options['CALL'] = options['contractSymbol'].str[4:].apply(lambda x: "C" in x)
    
    # Convert bid, ask, and strike to numeric
    options[['bid', 'ask', 'strike']] = options[['bid', 'ask', 'strike']].apply(pd.to_numeric)
    
    # Drop unnecessary columns
    options = options.drop(columns=['contractSize', 'currency', 'change', 'percentChange', 'lastTradeDate', 'lastPrice'])

    # If a specific contractSymbol is provided, filter for that contract
    if specific_contract:
        options = options[options['contractSymbol'] == specific_contract]
    
    return options

# Example usage:
symbol = 'AAPL'
specific_contract = 'AAPL240209C00125000'  # Example contract symbol
options = my_options_chain(symbol, specific_contract)
print("\n\n\n\n\n\n\n", options)