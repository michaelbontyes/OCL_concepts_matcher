import openpyxl
import json
import math
from rapidfuzz import process, fuzz
import pandas as pd

# Ignore potential warnings related to opening large Excel files
openpyxl.reader.excel.warnings.simplefilter(action='ignore')

# Excel Metadata filepath
metadata_filepath = "LIME EMR - Iraq Metadata - Release 1 (14).xlsx"

# Matching threshold for fuzzy string matching
FUZZY_THRESHOLD = 90

# Initialize the counter of concept to match
CONCEPTS_TO_MATCH = 0

# Initialize the counter of matches found above the threshold
MATCHES_FOUND = 0

# Define the sheets to read
# excel_sheets = [ 'FXX-Test_Only']

excel_sheets = [ 'F01-MHPSS Baseline', 'F02-MHPSS Follow-up', 'F03-mhGAP Baseline', 'F04-mhGAP Follow-up', 'F05-MH Closure', 'F06-PHQ-9', 'F07-ITFC form', 'F08-ATFC form', 'OptionSets']

# Define OCL sources and their respective columns in the Excel document
automatch_references = {
    "MSF": {
        "source_filepath": "MSF_Source_20240708_130415.json",
        "suggestion_column": "MSF Source Suggestion",
        "external_id_column": "MSF Source External ID",
        "description_column": "MSF Source Description",
        "datatype_column": "MSF Source Datatype",
        "dataclass_column": "MSF Source Class",
        "score_column": "MSF Source Score"
    },
    "CIEL": {
        "source_filepath": "CIEL_Source_20240708_153712.json",
        "suggestion_column": "CIEL Source Suggestion",
        "external_id_column": "CIEL Source External ID",
        "description_column": "CIEL Source Description",
        "datatype_column": "CIEL Source Datatype",
        "dataclass_column": "CIEL Source Class",
        "score_column": "CIEL Source Score"
    },
    "PIH": {
        "source_filepath": "PIH_Source_20240708_145352.json",
        "suggestion_column": "PIH Source Suggestion",
        "external_id_column": "PIH Source External ID",
        "description_column": "PIH Source Description",
        "datatype_column": "PIH Source Datatype",
        "dataclass_column": "PIH Source Class",
        "score_column": "PIH Source Score"
    }
}

# Find the best matches for each primary and secondary label in the metadata spreadsheet
def find_best_matches(primary, secondary, data, threshold=FUZZY_THRESHOLD, limit=5):
    """
    Find the best matches for a primary and secondary value from a list of data.

    :param primary: The primary value to search for
    :param secondary: The secondary value to search for
    :param data: List of dictionaries with 'id' (string) and 'display_name'
    :param limit: The maximum number of matches to return
    :return: List of tuples containing the id, match, score, and definition
    """
    # Combine the primary and secondary values into a single query string
    query = f"{primary} {secondary}"

    # Extract display_names from data for comparison
    display_names = [item['display_name'] for item in data]

    # Use rapidfuzz's process.extract to find the best matches with threshold
    matches = process.extract(query, display_names, scorer=fuzz.WRatio, score_cutoff=threshold, limit=limit)

    # Map the matches back to their corresponding IDs and definitions
    results = []
    for match, score, index in matches:
        print(f"Match: {match}, Score: {score}")
        if score >= FUZZY_THRESHOLD:
            external_id = data[index]['external_id']
            definition = data[index]['extras']['definition']
            results.append((external_id, match, score, definition))
            global MATCHES_FOUND
            MATCHES_FOUND += 1
            return results
    return []  # Return an empty list when there are no matches found above the threshold

# Open the metadata Excel file and find the column indices for the required columns
def find_column_index(worksheet, column_name):
    """
    Find the column index for the specified column name in the second row.

    Args:
    worksheet (openpyxl.worksheet.worksheet): The worksheet object.
    column_name (str): The name of the column to find the index for.

    Returns:
    int: The index of the specified column name in the second row.
    """
    for idx, cell in enumerate(worksheet[2], 1):  # assuming the second row contains headers
        if cell.value == column_name:
            return idx
    return -1  # Return -1 if the column name is not found

# Iterate through the sheets in df that are in the excel_sheets list with headers on row 2
for sheet_name in excel_sheets:

    # Iterate through each OCL source and look for suggestions for the primary and secondary lookups
    for source_name, source_config in automatch_references.items():
        print(f"Looking for suggestions in {source_name} source...")
        source_filepath = source_config['source_filepath']

        with open(source_filepath, 'r', encoding='UTF-8') as f:
            json_data = json.load(f)
            # Extract only the ID, display names, external IDs, datatype, concept_class, and extras > definitions from the JSON data
            source_data = []
            for item in json_data:
                concept_id = item.get('id', '')
                display_name = item.get('display_name', '')
                definition = item.get('extras', {}).get('definition', '')
                datatype = item.get('datatype')
                concept_class = item.get('concept_class')
                external_id = item.get('external_id')

                # Add the concept details to the source_data list
                source_data.append({
                    'id': concept_id,
                    'display_name': display_name,
                    'definition': definition,
                    'datatype': datatype,
                    'concept_class': concept_class,
                    'external_id': external_id,
                    'extras': {
                        'definition': definition
                    }
                })
            # Pretty print the display_names
            #print(json.dumps(display_names, indent=4))
            #print(f"Loaded {len(display_names)} concepts from {source_name}")

        # Load the Excel file, considering the header on row 2
        df = pd.read_excel(metadata_filepath, sheet_name=sheet_name, header=1)
        print(f"Processing sheet: {sheet_name}")

        # Load the existing Excel file to append the suggestions
        book = openpyxl.load_workbook(metadata_filepath)

        # Using Excel Writer, append or update the details in the original existing Excel sheet and cells in the specified columns depending on the source name
        with pd.ExcelWriter(metadata_filepath, engine='openpyxl', mode='a') as writer:
            workbook = writer.book
            worksheet = workbook[sheet_name]

            # Get the column indices for the suggestion, external ID, description, datatype, concept class, and extras
            suggestion_column = find_column_index(worksheet, source_config['suggestion_column'])
            external_id_column = find_column_index(worksheet, source_config['external_id_column'])
            description_column = find_column_index(worksheet, source_config['description_column'])
            datatype_column = find_column_index(worksheet, source_config['datatype_column'])
            dataclass_column = find_column_index(worksheet, source_config['dataclass_column'])
            score_column = find_column_index(worksheet, source_config['score_column'])

            # Iterate through each row in the sheet and get the Label if different if exist of nothing as a primary label to match, and the Question if exist or Answer if sheet is optionSets as secondary label to match
            for index, row in df.iterrows():
                CONCEPTS_TO_MATCH += 1
                primary_lookup = row.get('Label if different') or None
                secondary_lookup = row.get('Question') or row.get('Answers') or None
                #print(f"Processing row {index+1}: {primary_lookup} - {secondary_lookup}")

                # Get suggestions from each OCL source using closest match with RapidFuzz using the primary lookup and secondary lookups
                best_matches = find_best_matches(primary_lookup, secondary_lookup, source_data)
                # Print the results
                for id_, match, score, definition in best_matches:
                    print(f"Match found: ID: {id_}, Match: {match}, Score: {score}, Definition: {definition}")

                    # Get the column indices for the suggestion, external ID, description, datatype, concept class, and extras based on the column names in the source in the automatch_references
                    print(f"Updating row {index+3} with {suggestion_column}: {match}")
                    print(f"Updating row {index+3} with {external_id_column}: {external_id}")
                    print(f"Updating row {index+3} with {description_column}: {definition}")
                    print(f"Updating row {index+3} with {datatype_column}: {datatype}")
                    print(f"Updating row {index+3} with {dataclass_column}: {concept_class}")
                    print(f"Updating row {index+3} with {score_column}: {score}")

                    # Append the details to the existing Excel sheet
                    worksheet.cell(row=index+3, column=suggestion_column).value = match
                    worksheet.cell(row=index+3, column=external_id_column).value = external_id
                    worksheet.cell(row=index+3, column=description_column).value = definition
                    worksheet.cell(row=index+3, column=datatype_column).value = datatype
                    worksheet.cell(row=index+3, column=dataclass_column).value = concept_class
                    worksheet.cell(row=index+3, column=score_column).value = score

            # Close the Excel file writer
            workbook.close()

# Count of sources used
print(f"\nSources used: {len(automatch_references)}")

# Show the total number of concepts processed
CONCEPTS_TO_MATCH = math.ceil(CONCEPTS_TO_MATCH / len(automatch_references))
print(f"\nTotal concept processed: {CONCEPTS_TO_MATCH}")

# Show the total number of matches found above the threshold
percentage_found = (MATCHES_FOUND / CONCEPTS_TO_MATCH) * 100
rounded_percentage_found = math.ceil(percentage_found)
print(f"\nTotal matches found: {MATCHES_FOUND} ({rounded_percentage_found}%)")
