import requests
import json
from datetime import datetime

def fetch_all_concepts(api_url):
    total_concepts = 0
    page = 1
    concepts = []

    while True:
        response = requests.get(f"{api_url}&page={page}")
        if response.status_code == 200:
            data = response.json()
            concepts.extend(data)
            total_concepts += len(data)

            if not data:
                break

            page += 1
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            break

    print(f"Total concepts found: {total_concepts}")
    return concepts

# URL of the API without the page parameter
api_url = "https://api.openconceptlab.org/orgs/MSF/sources/MSF/concepts/?q=&limit=0"

# Fetch and print total concepts
concepts = fetch_all_concepts(api_url)
TOTAL_CONCEPTS = len(concepts)
print(f"Total number of concepts: {TOTAL_CONCEPTS}")

# Save the fetched concepts to a JSON file with a timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
file_path = f"concepts_{timestamp}.json"
with open(file_path, 'w') as file:
    json.dump(concepts, file)

print(f"Concepts saved to {file_path}")