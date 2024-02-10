import json

def extract_data_for_stock(stock_name, file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)

        if stock_name not in data:
            print(f"Stock {stock_name} not found in the file.")
            return None

        stock_data = data[stock_name]

        if "Optimized Top 10 14-day periods" in stock_data:
            periods = stock_data["Optimized Top 10 14-day periods"]
            optimized_data = []
            for period, details in periods.items():
                optimized_data.append({
                    "Period": period,
                    "Optimized Average Growth": details.get("Optimized Average Growth", 0)
                })

            return {
                "Years Processed": stock_data.get("Years Processed", "Unknown"),
                "Optimized Periods": optimized_data
            }

    except Exception as e:
        print(f"Error reading file: {e}")
        return None

# Example usage
file_path = 'split_0.json'  # Replace with your actual JSON file path
stock_name = 'AAPL'  # Replace with your desired stock name
extracted_data = extract_data_for_stock(stock_name, file_path)
print(extracted_data)
