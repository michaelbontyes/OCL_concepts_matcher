import pandas as pd
import json
from fuzzywuzzy import process

# Load the CSV file
csv_file_path = 'concepts.csv'
csv_data = pd.read_csv(csv_file_path, encoding='ISO-8859-1')

# Load the JSON file
json_file_path = 'concepts_20240625_150944.json'
with open(json_file_path, 'r') as json_file:
    json_data = json.load(json_file)

# Extract display names and external IDs from JSON data
display_names = [item['display_name'] for item in json_data]
external_ids = [item['external_id'] for item in json_data]

# Function to find the best match for a given label with a stricter threshold
def find_best_match(label, choices, threshold):
    label = str(label)  # Convert label to string
    best_match, score = process.extractOne(label, choices)
    print(f"Label: {label}, Match: {best_match}, Score: {score}")
    if score >= threshold:
        return best_match, score
    else:
        return None, None

# Apply the updated function to the CSV data
csv_data['Match'], csv_data['Score'] = zip(*csv_data['Label'].apply(lambda x: find_best_match(x, display_names, 95)))

# Remove rows where no match was found
csv_data = csv_data.dropna(subset=['Match'])

# Create a new column "External ID" in the CSV data
csv_data['External ID'] = csv_data['Match'].apply(lambda x: external_ids[display_names.index(x)] if x is not None else '')

# Save the updated CSV file
output_file_path = 'concepts_with_matches.csv'
csv_data.to_csv(output_file_path, index=False)

print(f"Updated CSV file saved as {output_file_path}")