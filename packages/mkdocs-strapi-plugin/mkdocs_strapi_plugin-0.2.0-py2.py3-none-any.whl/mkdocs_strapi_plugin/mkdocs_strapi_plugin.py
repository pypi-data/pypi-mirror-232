"""Main module."""
# Import necessary libraries
import requests
import mkdocs
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options

# Define the configuration options for your plugin
class StrapiPlugin(mkdocs.plugins.BasePlugin):
    config_scheme = (
        ("strapi_endpoint", mkdocs.config.config_options.Type(str, required=True, default=None)),
        ("content_type", mkdocs.config.config_options.Type(str, required=True, default=None)),
    )

class StrapiPluginConfig(mkdocs.plugins.BasePlugin):
    strapi_endpoint = mkdocs.config.config_options.Type(str, required=True, default='a default value'),
    content_type = mkdocs.config.config_options.Type(str, required=True, default='a default value'),

class Strapi(mkdocs.plugins.BasePlugin):
    def __init__(self, config):
        super().__init__(config)
        self.strapi_endpoint = config["strapi_endpoint"]
        self.content_type = config["content_type"]

    def on_config(self, config, **kwargs):
        # Get the data from the Strapi API
        response = requests.get(self.strapi_endpoint + self.content_type)
        # Convert the response to JSON
        data = response.json()
        # Add the data to the config
        config["strapi"] = data
        return config
    
    def on_page_markdown(self, markdown, page, config, files):
        # Get the data from the config
        data = config["strapi"]
        # Loop through the data
        for item in data:
            # Replace the markdown with the data
            markdown = markdown.replace(item["markdown"], item["content"])
        return markdown
    
    def on_page_content(self, html, page, config, files):

        # Get the data from the config
        page = page.file.src_path
        files = files.get_file(page)
        data = config["strapi"]
        # Loop through the data
        for item in data:
            # Replace the markdown with the data
            html = html.replace(item["markdown"], item["content"])
        return html
    
    def on_page_context(self, context, page, config, nav):
        # Get the data from the config
        page = page.file.src_path
        nav = nav.pages
        data = config["strapi"]
        # Add the data to the context
        context["strapi"] = data
        return context
        