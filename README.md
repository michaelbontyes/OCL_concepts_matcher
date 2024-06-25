![Python Lint and Test](https://github.com/michaelbontyes/OCL_concepts_matcher/actions/workflows/pylint.yml/badge.svg)

# Concepts Fetcher and Matcher for OpenConceptLab and MSF Source

## Prerequisites

- Python 3.x installed
- `requests` library installed (you can install it using `pip install requests`)
- `json` library installed (it's part of the Python standard library)

## Fetcher.py

The `fetcher.py` script fetches all concepts from the OpenConceptLab API and saves them to a JSON file with a timestamp.

### What it does

- Fetches concepts from the OpenConceptLab API using pagination.
- Saves the fetched concepts to a JSON file.

### How it works

1. The script defines a function `fetch_all_concepts` that takes the API URL as an argument.
2. Inside the function, it initializes variables for the total number of concepts, the current page, and an empty list to store the concepts.
3. It enters a loop that continues until there are no more pages of concepts to fetch.
4. Inside the loop, it makes a GET request to the API URL with the current page number.
5. If the request is successful (status code 200), it extracts the concepts from the response JSON and adds them to the list of concepts.
6. It also updates the total number of concepts and increments the page number.
7. If the request is not successful, it prints an error message with the status code.
8. After the loop, it prints the total number of concepts fetched.
9. It then saves the fetched concepts to a JSON file with a timestamp.

### Configurable

- You can modify the OCL URL in the `API_URL` variable to fetch concepts from a specific organization and source.

### Results

- Fetched concepts are saved to a JSON file named `concepts_YYYYMMDD_HHMMSS.json`, where `YYYYMMDD_HHMMSS` represents the current timestamp.

## Matcher.py

The `matcher.py` script reads a JSON file containing concepts, performs matching operations, and saves the results to another JSON file.

### What it does

- Reads concepts from an input JSON file.
- Performs matching operations on the concepts (this part is not implemented in the provided code).
- Saves the matched concepts to an output JSON file.

### How it works

1. The script defines a function `match_concepts` that takes the input JSON file path and the output JSON file path as arguments.
2. Inside the function, it reads the concepts from the input JSON file.
3. It performs matching operations on the concepts (this part is not implemented in the provided code).
4. It saves the matched concepts to the output JSON file.

### Results

- Matched concepts are saved to an output JSON file.

Note: The matching operations in the `matcher.py` script are not implemented in the provided code. You will need to add your own matching logic based on your specific requirements.