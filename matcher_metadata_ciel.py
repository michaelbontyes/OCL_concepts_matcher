import json
from multiprocessing import Pool
from rapidfuzz import process, fuzz
import pandas as pd

# Function to find the best match for a given label
def find_best_match(label, choices, threshold=95):
    """ Finds the best match for a given label with a stricter threshold. """
    label = str(label)  # Convert label to string
    matches = process.extract(label, choices, scorer=fuzz.WRatio, limit=5)
    if not matches:
        return None, None
    # Ensure the structure of matches is correct
    best_match_data = max(matches, key=lambda x: x[1])
    if len(best_match_data) < 2:
        return None, None
    best_match, score = best_match_data[:2]  # Unpack only the first two elements
    if score >= threshold:
        return best_match, score
    return None, None

# Function to process a batch of rows
# Function to process a batch of rows
def process_batch(df_batch, display_names, label_column, suggestion_column, score_column, external_id_column):
    matches_found = 0
    for index, row in df_batch.iterrows():
        if pd.notna(row[label_column]):
            match, score = find_best_match(row[label_column], display_names.keys())
            df_batch.at[index, suggestion_column] = match if match else None
            df_batch.at[index, score_column] = int(score) if score else 0  # Convert score to integer
            df_batch.at[index, external_id_column] = display_names.get(match, None) if match else None
            if score and score >= 95:
                matches_found += 1
                print(f"Label: {row[label_column]}, Match: {match}, Score: {score}")
    return df_batch, matches_found

def main():
    # Load the Excel file
    file_path = 'metadata.xlsx'
    xls = pd.ExcelFile(file_path)

    # Define the sheets and columns to be updated
    sheets = ['F01-MHPSS_Baseline', 'F02-MHPSS_Follow-up', 'OptionSets']
    label_column = 'Label'
    suggestion_column = 'CIEL Source Suggestion'
    score_column = 'CIEL Source Score'
    external_id_column = 'CIEL Source External ID'

    # Create a dictionary to hold the updated DataFrames
    updated_dfs = {}

    # Load the JSON file
    json_file_path = 'CIEL_Source_Filtered_20240626_115849.json'
    with open(json_file_path, 'r', encoding='ISO-8859-1') as f:
        json_data = json.load(f)
        display_names = {item['display_name']: item['external_id'] for item in json_data}

    # Initialize the counter of matches found above the threshold
    total_matches_found = 0

    # Process each sheet
    for sheet in sheets:
        # Load the sheet into a DataFrame
        df = pd.read_excel(xls, sheet_name=sheet, header=1)
        
        # Process the data in batches
        batch_size = 10000
        chunks = [df[i:i + batch_size] for i in range(0, len(df), batch_size)]
        
        # Use parallel processing
        with Pool() as pool:
            print(f"Processing sheet {label_column}...")
            results = pool.starmap(
                process_batch, 
                [(chunk, display_names, label_column, suggestion_column, score_column, external_id_column) for chunk in chunks]
            )
        
        # Collect the updated chunks and matches found
        updated_chunks = []
        for updated_chunk, matches_found in results:
            updated_chunks.append(updated_chunk)
            total_matches_found += matches_found
        
        # Concatenate the updated chunks
        df_updated = pd.concat(updated_chunks)
        
        # Save the updated DataFrame to a new file
        updated_dfs[sheet] = df_updated

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
    print(f"Number of matches found above the threshold: {total_matches_found}")

if __name__ == '__main__':
    main()