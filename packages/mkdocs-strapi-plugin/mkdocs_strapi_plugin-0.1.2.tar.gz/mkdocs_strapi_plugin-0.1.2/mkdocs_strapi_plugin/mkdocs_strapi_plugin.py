"""Main module."""
# Import necessary libraries
import requests
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options

# Define the configuration options for your plugin
class StrapiPlugin(BasePlugin):
    config_scheme = (
        ("strapi_url", config_options.Type(str, required=True, default=None)),
    )

    def __init__(self):
        self.strapi = None

    def on_config(self, config, **kwargs):
        self.strapi = Strapi(self.config["strapi_url"], self.config["auth_token"])

    def on_page_markdown(self, markdown, **kwargs):
        # Fetch data from the Strapi API
        data = self.strapi.fetch_data()

        # Replace placeholders in the markdown content with the fetched data
        markdown = markdown.replace("{{ data }}", str(data))

        return markdown

# A class for handling interactions with the Strapi API
class Strapi:
    def __init__(self, url):
        self.url = url

    def create_data(self, new_data):
        try:
            response = requests.post(self.url, json=new_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error creating data in Strapi API: {e}")
            return {}

    def fetch_data(self):
        try:
            # Send an HTTP GET request to the Strapi API
            response = requests.get(self.url)
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Parse the JSON response
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            # Handle any network errors or API request exceptions
            print(f"Error fetching data from Strapi API: {e}")
            return {}

    def get_data(self, id):
        try:
            response = requests.get(f"{self.url}/{id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from Strapi API: {e}")
            return {}
        
    def update_data(self, id, updated_data):
        try:
            response = requests.put(f"{self.url}/{id}", json=updated_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error updating data in Strapi API: {e}")
            return {}
        
    def delete_data(self, id):
        try:
            response = requests.delete(f"{self.url}/{id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error deleting data in Strapi API: {e}")
            return {}
    
    def search_data(self, search_term):
        try:
            response = requests.get(f"{self.url}?q={search_term}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error searching data in Strapi API: {e}")
            return {}
        