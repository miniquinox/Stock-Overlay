import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

def stock_overlay(stock_name, start_date, end_date):
    # Convert start_date and end_date to YYYY-MM-DD format if necessary
    start_date = pd.to_datetime(start_date).strftime('%Y-%m-%d')
    end_date = pd.to_datetime(end_date).strftime('%Y-%m-%d')

    # Download historical data for the stock
    stock_data = yf.download(stock_name, start=start_date, end=end_date)

    # Function to align all dates to the same year for plotting
    def align_dates_to_same_year(dates, year=2020):
        return dates.map(lambda x: x.replace(year=year))

    # Prepare the figure and axis
    plt.figure(figsize=(15, 8))
    ax = plt.gca()

    # Calculate and plot YTD percentage growth for each year
    start_year = pd.to_datetime(start_date).year
    end_year = pd.to_datetime(end_date).year + 1  # Include the end year in the range

    for year in range(start_year, end_year):
        # Extract the year's data
        year_data = stock_data.loc[f"{year}-01-01":f"{year}-12-31"]

        if not year_data.empty:
            # Calculate the YTD growth percentage
            year_start_price = year_data.iloc[0]['Adj Close']
            year_data['YTD Growth'] = (year_data['Adj Close'] - year_start_price) / year_start_price * 100

            # Align the index for overlaying
            year_data.index = align_dates_to_same_year(year_data.index)

            # Plot the data
            ax.plot(year_data.index, year_data['YTD Growth'], label=str(year))

    # Set the x-axis major formatter to show month and day
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))

    # Set other plot properties
    plt.title(f'Year-to-Date Growth of {stock_name} Stock ({start_year}-{end_year - 1}) Overlaid')
    plt.xlabel('Date (Aligned to Same Year)')
    plt.ylabel('Percentage Growth (%)')
    plt.legend(title='Year')
    plt.grid(True)

    # Tight layout to ensure everything fits without overlapping
    plt.tight_layout()

    # Show the plot
    plt.show()

# Main section
if __name__ == "__main__":
    stock_name = "META"
    start_date = "01-01-2010"  # This could be in format "MM/DD/YYYY" as well
    end_date = "11-17-2023"
    stock_overlay(stock_name, start_date, end_date)
