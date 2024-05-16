import os
import json
import requests


# Assuming the JSON content is stored in a variable named 'films_json'
json_file_path: str = os.path.join(os.getcwd(), "films.json")

# Load the JSON content from the file
with open(json_file_path, "r") as file:
    films_json: dict = json.load(file)

# URL of the endpoint
endpoint_url = "http://127.0.0.1:8000/site-admin/add-film/"

for film_data in films_json["films"]:
    print()
    print(json.dumps(film_data, indent=4))
    response: requests.Response = requests.post(endpoint_url, json=film_data)
    if response.status_code == 201:
        print(response.json()["detail"])
    else:
        print(f"Failed to add film '{film_data['name']}':")
        print(json.dumps(dict(response.headers), indent=4))
        print(f"{json.dumps(response.json(), indent=4)}")
