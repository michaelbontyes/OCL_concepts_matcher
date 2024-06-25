"""
Fetches all concepts from the OpenConceptLab API and returns them as a list.
"""
from datetime import datetime
import json
import requests

def fetch_all_concepts(url):
    """
        Fetches all concepts from the OpenConceptLab API and returns them as a list.
    Args:
        url (str): The URL of the API without the page parameter.
    Returns:
        list: A list of all concepts fetched from the API.
    """
    total_concepts = 0
    page = 1
    concepts = []

    while True:
        response = requests.get(f"{url}&page={page}", timeout=5)
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
API_URL = "https://api.openconceptlab.org/orgs/MSF/sources/MSF/concepts/?q=&limit=0"

# Fetch and print total concepts
all_concepts = fetch_all_concepts(API_URL)
TOTAL_CONCEPTS = len(all_concepts)
print(f"Total number of concepts: {TOTAL_CONCEPTS}")

# Save the fetched concepts to a JSON file with a timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
file_path = f"concepts_{timestamp}.json"
with open(file_path, 'w', encoding='utf-8') as file:
    json.dump(all_concepts, file)

print(f"Concepts saved to {file_path}")
