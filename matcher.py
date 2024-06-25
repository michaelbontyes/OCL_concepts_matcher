""" Finds the best match for a given concept label with a strict threshold. """
import json
import pandas as pd
from fuzzywuzzy import process

# Load the CSV file
CSV_FILE_PATH = 'concepts.csv'
csv_data = pd.read_csv(CSV_FILE_PATH, encoding='ISO-8859-1')

# Load the JSON file
JSON_FILE_PATH = 'concepts_20240625_150944.json'
with open(JSON_FILE_PATH, 'r', encoding='ISO-8859-1') as json_file:
    json_data = json.load(json_file)

# Extract display names and external IDs from JSON data
display_names = [item['display_name'] for item in json_data]
external_ids = [item['external_id'] for item in json_data]

# Function to find the best match for a given label with a stricter threshold
def find_best_match(label, choices, threshold):
    """ Finds the best match for a given label with a stricter threshold. """
    label = str(label)  # Convert label to string
    best_match, score = process.extractOne(label, choices)
    print(f"Label: {label}, Match: {best_match}, Score: {score}")
    if score >= threshold:
        return best_match, score
    return None, None

# Apply the updated function to the CSV data
csv_data['Match'], csv_data['Score'] = zip(*csv_data['Label'].apply(
    lambda x: find_best_match(x, display_names, 95)))

# Remove rows where no match was found
csv_data = csv_data.dropna(subset=['Match'])

# Create a new column "External ID" in the CSV data
csv_data['External ID'] = csv_data['Match'].apply(
    lambda x: external_ids[display_names.index(x)] if x is not None else '')

# Save the updated CSV file
OUTPUT_FILE_PATH = 'concepts_with_matches.csv'
csv_data.to_csv(OUTPUT_FILE_PATH, index=False)

print(f"Updated CSV file saved as {OUTPUT_FILE_PATH}")
