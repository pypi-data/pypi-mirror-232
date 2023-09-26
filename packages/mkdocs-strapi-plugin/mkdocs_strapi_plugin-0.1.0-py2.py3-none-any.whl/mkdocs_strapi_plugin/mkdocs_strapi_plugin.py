"""Main module."""
# Import necessary libraries
import requests
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options

# Define the configuration options for your plugin
class StrapiPlugin(BasePlugin):
    config_scheme = (
        ("strapi_url", config_options.Type(str, required=True, default=None)),
        # You can add more configuration options here, like authentication tokens, etc.
    )

    # Initialize the plugin
    def __init__(self):
        self.strapi = None

    # Called when the plugin is configured
    def on_config(self, config, **kwargs):
        # Initialize the Strapi object with the provided URL
        self.strapi = Strapi(self.config["strapi_url"])

    # Called when generating page markdown
    def on_page_markdown(self, markdown, **kwargs):
        # Fetch data from the Strapi API
        data = self.strapi.fetch_data()
        
        # for replacing placeholders in the markdown content with the fetched data
        markdown = markdown.replace("{{ data }}", str(data))

        return markdown

# A class for handling interactions with the Strapi API
class Strapi:
    def __init__(self, url):
        self.url = url

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
    
    def create_data(self, data):
        try:
            response = requests.post(self.url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error creating data in Strapi API: {e}")
            return {}