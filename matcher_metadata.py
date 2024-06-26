import json
import pandas as pd
from fuzzywuzzy import process

# Load the Excel file
file_path = 'metadata.xlsx'
xls = pd.ExcelFile(file_path)

# Define the sheets and columns to be updated
sheets = ['F01-MHPSS_Baseline', 'F02-MHPSS_Follow-up', 'OptionSets']
# sheets = ['F01-MHPSS_Baseline']
label_column = 'Label'
suggestion_column = 'MSF Source Suggestion'
score_column = 'MSF Source Score'
external_id_column = 'MSF Source External ID'

# Create a dictionary to hold the updated DataFrames
updated_dfs = {}

# Load the JSON file
json_file_path = 'CIEL_Source_Filtered_20240626_115849.json'
with open(json_file_path, 'r', encoding='ISO-8859-1') as json_file:
    json_data = json.load(json_file)

# Extract display names and external IDs from JSON data
display_names = [item['display_name'] for item in json_data]
external_ids = [item['external_id'] for item in json_data]

# Initialize the counter of matches found above the threshold
matches_found = 0

# Function to find the best match for a given label
def find_best_match(label, choices, threshold=95):
    """ Finds the best match for a given label with a stricter threshold. """
    label = str(label)  # Convert label to string
    best_match, score = process.extractOne(label, choices)
    if score >= threshold:
        print(f"Label: {label}, Match: {best_match}, Score: {score}")
        global matches_found
        matches_found += 1
        return best_match, score
    return None, None

# Process each sheet
for sheet in sheets:
    # Load the sheet into a DataFrame
    df = pd.read_excel(xls, sheet_name=sheet, header=1)
    
    # Check and update the columns
    if label_column in df.columns and suggestion_column in df.columns and score_column in df.columns and external_id_column in df.columns:
        for index, row in df.iterrows():
            if pd.notna(row[label_column]):
                #print(f"Updating row {row[label_column]} in sheet {sheet}...")
                match, score = find_best_match(row[label_column], display_names)
                df.at[index, label_column] = row[label_column]
                df.at[index, suggestion_column] = match if match else ''
                df.at[index, score_column] = score if score else ''
                df.at[index, external_id_column] = external_ids[display_names.index(match)] if match else ''
    
    # Save the updated DataFrame to a new file
    updated_dfs[sheet] = df

# Save the updated DataFrames back to the new Excel file using openpyxl engine
updated_file_path = 'metadata_updated.xlsx'
with pd.ExcelWriter(updated_file_path, engine='openpyxl', mode='w') as writer:
    for sheet, df in updated_dfs.items():
        df.to_excel(writer, sheet_name=sheet, index=False)

# Load the updated Excel file to check the modifications
xls_updated = pd.ExcelFile(updated_file_path)
updated_sheets = {sheet: pd.read_excel(xls_updated, sheet_name=sheet) for sheet in sheets}

# Display the updated DataFrame to the user and the number of matches found above the threshold
print(updated_sheets)
print(f"Number of matches found above the threshold: {matches_found}")