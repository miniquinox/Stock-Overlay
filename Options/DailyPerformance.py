import json

# Load JSON data
with open('options_data.json', 'r') as file:
    data = json.load(file)

# Get the last date from the JSON data
last_date = sorted(data.keys())[-1]
options_data = data[last_date]

# Prepare the content to be appended to the README
content_to_append = f"### {last_date}\n\n"
content_to_append += "| Option ID | Performance |\n"
content_to_append += "| --- | --- |\n"

for option_id, details in options_data.items():
    open_price = details["Option Open Price"]
    max_price = details["Max Day Call Price"]
    
    # Calculate performance
    if open_price > 0:  # Avoid division by zero
        performance = ((max_price - open_price) / open_price) * 100
        if performance < 50:
            performance_str = f"🔴 {performance:.2f}% (DID NOT REACH 50%. Consider -20%)"
        else:
            performance_str = f"🟢 {performance:.2f}%"
    else:
        performance_str = "N/A"

    content_to_append += f"| {option_id} | Open @ {open_price} -> Max @ {max_price} = {performance_str} |\n"

# Append the content to the README file
with open('README.md', 'a') as readme_file:
    readme_file.write(content_to_append + "\n")

print("Appended new data to README.md.")
