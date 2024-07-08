import json
from multiprocessing import Pool
from rapidfuzz import process, fuzz
import pandas as pd

# Function to find the best match for a given label
def find_best_match(label, choices, threshold=90):
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
def process_batch(df_batch, display_names, label_column, suggestion_columns, score_columns, external_id_columns):
    matches_found = 0
    print(f"Processing batch with {len(df_batch)} rows...")
    for index, row in df_batch.iterrows():
        if pd.notna(row[label_column]):
            for i, (suggestion_column, score_column, external_id_column) in enumerate(zip(suggestion_columns, score_columns, external_id_columns)):
                match, score = find_best_match(row[label_column], display_names[i].keys())
                df_batch.at[index, suggestion_column] = match if match else None
                df_batch.at[index, score_column] = int(score) if score else ''  # Convert score to integer
                df_batch.at[index, external_id_column] = display_names[i].get(match, None) if match else None
                if score and score >= 90:
                    matches_found += 1
                    print(f"Label: {row[label_column]}, Match: {match}, Score: {score}")
    return df_batch, matches_found

def main():
    # Load the Excel file
    file_path = 'LIME EMR - Iraq Metadata - Release 1 (11).xlsx'
    xls = pd.ExcelFile(file_path)

    # Define the sheets and columns to be updated
    sheets = ['F01-MHPSS Baseline', 'F02-MHPSS Follow-up']
    label_column = 'Label'
    references = {
        "MSF": {
            "filepath": "MSF_Source_Filtered_20240704_161129.json",
            "suggestion_column": "MSF Source Suggestion",
            "score_column": "MSF Source Score",
            "external_id_column": "MSF Source External ID"
        }
    }

    # Initialize a list to store all updated DataFrames
    all_updated_chunks = []

    # Process each sheet
    for source, reference in references.items():
        print(f"Processing source: {source}...")
        # Load the JSON reference for the current source
        json_file_path = reference["filepath"]
        with open(json_file_path, 'r', encoding='UTF-8') as f:
            json_data = json.load(f)
            display_names = {item['display_name']: item['external_id'] for item in json_data}
            print(f"Loaded {len(display_names)} concepts from {json_file_path}")

        suggestion_columns = [reference["suggestion_column"]]
        score_columns = [reference["score_column"]]
        external_id_columns = [reference["external_id_column"]]

        # Initialize the counter of matches found above the threshold
        total_matches_found = 0

        # Process each sheet
        for sheet in sheets:
            print(f"Processing sheet {sheet}...")
            # Load the sheet into a DataFrame
            df = pd.read_excel(xls, sheet_name=sheet, header=1)

            # Process the data in batches
            batch_size = 10000
            chunks = [df[i:i + batch_size] for i in range(0, len(df), batch_size)]

            # Use parallel processing
            with Pool() as pool:
                results = pool.starmap(
                    process_batch, 
                    [(chunk, [display_names], label_column, suggestion_columns, score_columns, external_id_columns) for chunk in chunks]
                )

            # Collect the updated chunks and matches found
            updated_chunks = []
            for updated_chunk, matches_found in results:
                updated_chunks.append(updated_chunk)
                total_matches_found += matches_found

            # Concatenate the updated chunks
            df_updated = pd.concat(updated_chunks)

            # Collect the updated chunks and matches found
            all_updated_chunks.append(df_updated)

        # Update the cells in the original workbook
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='a') as writer:
            workbook = writer.book
            worksheet = workbook[sheet]
            for df_updated in all_updated_chunks:
                column_indices = {
                    suggestion_columns[0]: df_updated.columns.get_loc(suggestion_columns[0]) + 1,
                    score_columns[0]: df_updated.columns.get_loc(score_columns[0]) + 1,
                    external_id_columns[0]: df_updated.columns.get_loc(external_id_columns[0]) + 1
                }
                for index, row in df_updated.iterrows():
                    suggestion_value = row[suggestion_columns[0]] if row[suggestion_columns[0]] is not None else ''
                    score_value = row[score_columns[0]] if row[score_columns[0]] is not None else ''
                    external_id_value = row[external_id_columns[0]] if row[external_id_columns[0]] is not None else ''

                    print(f"Row {index+3}: {suggestion_columns[0]} = {suggestion_value}, {score_columns[0]} = {score_value}, {external_id_columns[0]} = {external_id_value}")

                    worksheet.cell(row=index+3, column=column_indices[suggestion_columns[0]]).value = suggestion_value
                    worksheet.cell(row=index+3, column=column_indices[score_columns[0]]).value = score_value
                    worksheet.cell(row=index+3, column=column_indices[external_id_columns[0]]).value = external_id_value

        print(f"Total matches found for source {source}: {total_matches_found}")

if __name__ == '__main__':
    main()