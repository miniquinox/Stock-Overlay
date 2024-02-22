# README for Stock Options Analysis Scripts

## Overview

These scripts are designed to automate the process of analyzing stock options by leveraging both web scraping and financial data APIs. The primary goal is to identify high-volatility stocks after market hours and predict the best option prices for these stocks before the market opens. The process involves two main steps: 

1. **Pre-market Analysis**: Run every weekday at 6:25 AM PST before the market opens, this step involves fetching data on stock prices and calculating predicted option prices for stocks showing high volatility after hours.
2. **Post-market Data Gathering**: Executed at 2:30 PM PST after the market closes, this step updates the analysis with actual market performance, comparing the predictions made in the morning with the day's high values for both stock and option prices.

## Dependencies

- Python 3.x
- Libraries: `yfinance`, `mibian`, `selenium`, `webdriver_manager`, `numpy`, `scipy`, `json`, `datetime`, `re`, `os`, `sys`

## Setup

Ensure Python 3.x is installed on your system. Install the necessary Python libraries using pip:

```bash
pip install yfinance mibian selenium webdriver_manager numpy scipy
```

Note: Selenium requires a WebDriver to interface with the chosen browser. `webdriver_manager` automatically handles driver management for Chrome.

## Scripts Description

### 1. Pre-market Analysis Script

#### Functionality

- Scrapes stock data from a specified website using Selenium to identify stocks with significant after-hours volatility.
- Filters stocks based on after-hours percentage change and market cap.
- Uses `yfinance` to fetch option data for the filtered stocks, focusing on call options.
- Calculates the predicted option prices for the next market opening using the Black-Scholes model and other financial metrics.
- Saves the analysis to a JSON file (`options_data.json`), including stock prices at market close, before market open, and predicted option prices.

#### How to Run

Scheduled to execute automatically at 6:25 AM PST every weekday using a cron job or a similar scheduler. Ensure the system is set up to match the Pacific Standard Time zone.

### 2. Post-market Data Gathering Script

#### Functionality

- Loads the pre-market analysis results from `options_data.json`.
- Updates the dataset with the actual maximum stock price and call option price for the day.
- This helps in evaluating the accuracy of the pre-market predictions by comparing them against the actual market performance.

#### How to Run

Scheduled to run at 2:30 PM PST after the market closes, ensuring that the day's trading data is fully available for analysis.

## Goal

The main objective of these scripts is to provide an automated toolset for financial analysts and traders focusing on high-volatility stocks. By predicting option prices before market opens and then comparing those predictions with actual outcomes, users can refine their strategies for option trading based on post-market volatility.

## Caution

These scripts involve financial data and predictions. Users should use this information as part of a broader analysis and not as the sole basis for any trading decisions. Financial markets are unpredictable, and there is always a risk of loss when trading.
  
  
## Options Daily Performance
  
### 1998-02-28

| Option ID | Performance |
| --- | --- |
| AMZN $3300.0 Call 2024-02-25 | 🔴 36.46% (DID NOT REACH 50%. Consider -20%) |
| GOOGL $2800.0 Call 2024-02-25 | 🟢 93.30% |
| NFLX $550.0 Call 2024-02-25 | 🟢 87.57% |

