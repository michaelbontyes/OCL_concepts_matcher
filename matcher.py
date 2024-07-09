import openpyxl
import json
from rapidfuzz import process, fuzz
import pandas as pd

# Ignore potential warnings related to opening large Excel files
openpyxl.reader.excel.warnings.simplefilter(action='ignore')

# Excel Metadata filepath
metadata_filepath = "LIME EMR - Iraq Metadata - Release 1 (12).xlsx"

# Matching threshold for fuzzy string matching
FUZZY_THRESHOLD = 90

# Initialize the counter of matches found above the threshold
MATCHES_FOUND = 0

# Define the sheets to read
excel_sheets = [ 'F01-MHPSS Baseline']

# excel_sheets = [ 'F01-MHPSS Baseline', 'F02-MHPSS Follow-up', 'F03-mhGAP Baseline', 'F04-mhGAP Follow-up', 'F05-MH Closure', 'F06-PHQ-9', 'F07-ITFC form', 'F08-ATFC form', 'OptionSets']

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
    }
}

# Find the best matches for each primary and secondary label in the metadata spreadsheet
def find_best_matches(primary, secondary, data, limit=5):
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

    # Use rapidfuzz's process.extract to find the best matches
    matches = process.extract(query, display_names, limit=limit)

    # Map the matches back to their corresponding IDs and definitions
    results = []
    for match, score, index in matches:
        if score > FUZZY_THRESHOLD:
            external_id = data[index]['external_id']
            definition = data[index]['extras']['definition']
            results.append((external_id, match, score, definition))
            global MATCHES_FOUND
            MATCHES_FOUND += 1
            return results
    return []  # Return an empty list when there are no matches found above the threshold

# Iterate through the sheets in df that are in the excel_sheets list with headers on row 2
for sheet_name in excel_sheets:
    # Load the Excel file, considering the header on row 2
    df = pd.read_excel(metadata_filepath, sheet_name=sheet_name, header=1)
    print(f"Processing sheet: {sheet_name}")

    # Iterate through each OCL source and look for suggestions for the primary and secondary lookups
    for source_name, source_config in automatch_references.items():
        print(f"Looking for suggestions in {source_name} source...")
        source_filepath = source_config['source_filepath']
        suggestion_column = source_config['suggestion_column']
        external_id_column = source_config['external_id_column']
        description_column = source_config['description_column']
        datatype_column = source_config['datatype_column']
        dataclass_column = source_config['dataclass_column']
        score_column = source_config['score_column']

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

        # Iterate through each row in the sheet and get the Label if different if exist of nothing as a primary label to match, and the Question if exist or Answer if sheet is optionSets as secondary label to match
        for index, row in df.iterrows():
            primary_lookup = row.get('Label if different') or None
            secondary_lookup = row.get('Question') or row.get('Answers') or None
            #print(f"Processing row {index+1}: {primary_lookup} - {secondary_lookup}")

            # Get suggestions from each OCL source using closest match with RapidFuzz using the primary lookup and secondary lookups
            best_matches = find_best_matches(primary_lookup, secondary_lookup, source_data)
            # Print the results
            for id_, match, score, definition in best_matches:
                    print(f"Match found: ID: {id_}, Match: {match}, Score: {score}, Definition: {definition}")

# Show the total number of matches found above the threshold
print(f"\nTotal matches found: {MATCHES_FOUND}")
