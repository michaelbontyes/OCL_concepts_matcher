import json

# Define source and target file paths
source_file = 'MSF_Source_20240704_161129.json'
filtered_file = 'MSF_Source_Filtered_20240704_161129.json'

# Initialize an empty list to hold the filtered data
filtered_data = []

# Open the source file and read it incrementally
with open(source_file, 'r', encoding='utf-8') as file:
    for line in file:
        try:
            # Parse each line as a JSON object
            concept = json.loads(line.strip(',\n'))  # Handle potential trailing commas and newlines
            # Extract the required fields
            filtered_concept = {
                'uuid': concept.get('uuid'),
                'id': concept.get('id'),
                'external_id': concept.get('external_id'),
                'display_name': concept.get('display_name'),
                'datatype': concept.get('datatype'),
                'concept_class': concept.get('concept_class'),
                'display_locale': concept.get('display_locale'),
                'URL': concept.get('url')
            }
            # Append the filtered concept to the list
            filtered_data.append(filtered_concept)
        except json.JSONDecodeError:
            continue  # Skip lines that cannot be parsed

# Save the filtered data to a new JSON file
with open(filtered_file, 'w', encoding='utf-8') as file:
    json.dump(filtered_data, file, indent=4)

print(f"Filtered data saved to {filtered_file}")