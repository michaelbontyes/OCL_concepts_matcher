import ijson
import requests
import json
from datetime import datetime

def fetch_all_concepts(url, file_path):
    total_concepts = 0
    page = 1
    is_first_page = True

    while True:
        response = requests.get(f"{url}&page={page}", timeout=30)  # Increased timeout duration to 30 seconds
        if response.status_code == 200:
            data = response.json()
            total_concepts += len(data)

            if not data:
                break

            with open(file_path, 'a', encoding='utf-8') as file:
                if is_first_page:
                    file.write("[\n")
                    is_first_page = False
                else:
                    file.write(",\n")
                
                for i, concept in enumerate(data):
                    json.dump(concept, file)
                    if i < len(data) - 1:
                        file.write(",\n")
            
            print(f"Total concepts found so far: {total_concepts}")
            page += 1
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            break

    with open(file_path, 'a', encoding='utf-8') as file:
        file.write("\n]")

    print(f"Total concepts found: {total_concepts}")
    return total_concepts

# URL of the API without the page parameter
API_URL = "https://api.openconceptlab.org/orgs/CIEL/sources/CIEL/concepts/?q=&limit=0"

# Save the fetched concepts to a JSON file with a timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
file_path = f"concepts_{timestamp}.json"

# Fetch and save total concepts incrementally
total_concepts = fetch_all_concepts(API_URL, file_path)
print(f"Total number of concepts: {total_concepts}")
print(f"Concepts saved to {file_path}")
