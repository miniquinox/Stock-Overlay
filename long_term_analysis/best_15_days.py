import yfinance as yf
import pandas as pd
import json
from datetime import datetime
from pandas.tseries.offsets import Day
from datetime import timedelta

def get_stock_launch_date(stock_name):
    try:
        stock_data = yf.download(stock_name, period="max", progress=False)
        return stock_data.index.min()
    except Exception as e:
        print(f"Failed to download {stock_name}: {e}")
        return None

# Function to check if a year is a leap year
def is_leap_year(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

def find_best_14_day_periods(stock_name, start_date, end_date):
    try:
        stock_data = yf.download(stock_name, start=start_date, end=end_date)
        if stock_data.empty:
            return None

        period_growth = {}

        # Iterate over each year in the stock data
        for year in range(stock_data.index.year.min(), stock_data.index.year.max() + 1):
            yearly_data = stock_data['Adj Close'][stock_data.index.year == year]
            start_of_year = datetime(year, 1, 1)
            end_of_year = datetime(year, 12, 31)

            # Iterate over each day in the year
            current_date = start_of_year
            while current_date <= end_of_year:
                # Skip the loop iteration if current_date is February 29th
                if is_leap_year(year) and current_date == datetime(year, 2, 29):
                    current_date += timedelta(days=1)

                # Calculate the end window date normally
                end_window_date = current_date + timedelta(days=13)

                # Check if February 29th falls within the period and adjust if necessary
                if is_leap_year(year) and current_date < datetime(year, 2, 29) <= end_window_date:
                    end_window_date += timedelta(days=1)

                # Find the closest trading day for start and end dates
                start_trading_date = find_closest_trading_day(yearly_data, current_date, forward=True)
                end_trading_date = find_closest_trading_day(yearly_data, end_window_date, forward=False)

                if start_trading_date and end_trading_date:
                    period_label = f"{current_date.strftime('%m-%d')} to {end_window_date.strftime('%m-%d')}"
                    start_price = yearly_data.loc[start_trading_date]
                    end_price = yearly_data.loc[end_trading_date]
                    growth = (end_price - start_price) / start_price

                    if period_label not in period_growth:
                        period_growth[period_label] = {}
                    period_growth[period_label][year] = growth

                current_date += timedelta(days=1)

        # Calculate the average growth for each period over the years
        average_growth = {period: sum(values.values()) / len(values) for period, values in period_growth.items()}

        # Sort and select the top 10 periods based on average growth
        sorted_periods = sorted(average_growth.items(), key=lambda x: x[1], reverse=True)[:10]

        # Include yearly growth for top periods
        top_periods = {period: {"Average Growth": avg_growth, "Yearly Growth": period_growth[period]} for period, avg_growth in sorted_periods}
        
        return top_periods

    except Exception as e:
        print(f"Failed to download {stock_name}: {e}")
        return None


def find_closest_trading_day(data, target_date, forward=True):
    """
    Find the closest trading day to the target_date.
    If forward is True, search forward in time, otherwise search backward.
    """
    if target_date in data.index:
        return target_date
    elif forward:
        while target_date <= data.index.max():
            target_date += timedelta(days=1)
            if target_date in data.index:
                return target_date
    else:
        while target_date >= data.index.min():
            target_date -= timedelta(days=1)
            if target_date in data.index:
                return target_date
    return None

def find_best_optimized_14_day_periods(stock_name, start_date, end_date):
    try:
        stock_data = yf.download(stock_name, start=start_date, end=end_date)
        if stock_data.empty:
            return None

        period_growth = {}

        # Iterate over each year in the stock data
        for year in range(stock_data.index.year.min(), stock_data.index.year.max() + 1):
            yearly_data = stock_data['Adj Close'][stock_data.index.year == year]
            start_of_year = datetime(year, 1, 1)
            end_of_year = datetime(year, 12, 31)

            # Iterate over each day in the year
            current_date = start_of_year
            while current_date <= end_of_year:
                # Skip the loop iteration if current_date is February 29th
                if is_leap_year(year) and current_date == datetime(year, 2, 29):
                    current_date += timedelta(days=1)

                # Calculate the end window date normally
                end_window_date = current_date + timedelta(days=13)

                # Check if February 29th falls within the period and adjust if necessary
                if is_leap_year(year) and current_date < datetime(year, 2, 29) <= end_window_date:
                    end_window_date += timedelta(days=1)

                # Find the closest trading day for start and end dates
                start_trading_date = find_closest_trading_day(yearly_data, current_date, forward=True)
                end_trading_date = find_closest_trading_day(yearly_data, end_window_date, forward=False)

                if start_trading_date and end_trading_date:
                    period_label = f"{current_date.strftime('%m-%d')} to {end_window_date.strftime('%m-%d')}"
                    start_price = yearly_data.loc[start_trading_date]
                    end_price = yearly_data.loc[end_trading_date]
                    growth = (end_price - start_price) / start_price

                    if period_label not in period_growth:
                        period_growth[period_label] = {}
                    period_growth[period_label][year] = growth

                current_date += timedelta(days=1)

        # Optimizing growth by removing the max and min values for each period
        optimized_growth = {}
        for period, yearly_values in period_growth.items():
            yearly_values_sorted = sorted(yearly_values.items(), key=lambda x: x[1])
            if len(yearly_values_sorted) > 2:
                # Remove the maximum and minimum values
                yearly_values_sorted.pop()
                yearly_values_sorted.pop(0)
                optimized_growth[period] = dict(yearly_values_sorted)
            else:
                optimized_growth[period] = dict(yearly_values_sorted)

        # Calculate the average growth for each period over the years
        average_growth = {period: sum(values.values()) / len(values) for period, values in optimized_growth.items()}

        # Sort and select the top 10 periods based on average growth
        sorted_periods = sorted(average_growth.items(), key=lambda x: x[1], reverse=True)[:10]

        # Include yearly growth for top periods
        top_periods = {period: {"Optimized Average Growth": avg_growth, "Yearly Growth": optimized_growth[period]} for period, avg_growth in sorted_periods}
        
        return top_periods

    except Exception as e:
        print(f"Failed to download {stock_name}: {e}")
        return None



def find_consistent_periods(original_periods, optimized_periods):
    # Compare both sets of periods and find consistent ones
    consistent_periods = original_periods.index.intersection(optimized_periods.index)
    return consistent_periods

# New function to write results to a JSON file
def write_to_json(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

if __name__ == "__main__":
    # Load stocks from a JSON file
    with open('stocks.json', 'r') as file:
        stock_data = json.load(file)

    stocks = stock_data['Stocks']
    results = {}
    skipped_stocks = []
    stock_counter = 0

    for stock in stocks:
        stock_counter += 1
        print(f"Processing stock {stock_counter}/{len(stocks)}: {stock}")

        launch_date = get_stock_launch_date(stock)
        if launch_date is None:
            print(f"Failed to get launch date for {stock}, skipping...")
            skipped_stocks.append(stock)
            continue

        if isinstance(launch_date, datetime) and launch_date > datetime(2019, 1, 1):
            print(f"{stock} was launched after Jan 1st, 2019, skipping...")
            skipped_stocks.append(stock)
            continue

        years_processed = min(datetime.now().year - launch_date.year, 10)

        start_date = "2010-01-01"
        end_date = "2023-11-22"

        top_periods_dict = find_best_14_day_periods(stock, start_date, end_date)
        if top_periods_dict is None:
            print(f"Failed to calculate top periods for {stock}, skipping...")
            skipped_stocks.append(stock)
            continue

        optimized_top_periods_dict = find_best_optimized_14_day_periods(stock, start_date, end_date)
        if optimized_top_periods_dict is None:
            print(f"Failed to calculate optimized top periods for {stock}, skipping...")
            skipped_stocks.append(stock)
            continue

        consistent_periods = find_consistent_periods(pd.Series(top_periods_dict), pd.Series(optimized_top_periods_dict)).tolist()

        results[stock] = {
            "Years Processed": f"{years_processed} years",
            "Top 10 14-day periods": top_periods_dict,
            "Optimized Top 10 14-day periods": optimized_top_periods_dict,
            "Consistent 14-day periods": consistent_periods
        }

    # Write results to JSON file
    write_to_json('10_day_stocks.json', results)

    if skipped_stocks:
        print("Skipped stocks:")
        for stock in skipped_stocks:
            print(stock)
