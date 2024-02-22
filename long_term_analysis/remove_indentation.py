import json

def split_and_remove_indentation(json_file_path, split_size=100):
    # Reading the JSON file
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    # Splitting the top-level keys into chunks of 100
    keys = list(data.keys())
    chunks = [keys[i:i + split_size] for i in range(0, len(keys), split_size)]

    # Saving each chunk to a separate file without indentation
    for index, chunk in enumerate(chunks):
        chunk_data = {key: data[key] for key in chunk}
        with open(f'split_{index}.json', 'w') as file:
            json.dump(chunk_data, file, indent=None)

# Example usage:
split_and_remove_indentation('10_day_stocks.json')
