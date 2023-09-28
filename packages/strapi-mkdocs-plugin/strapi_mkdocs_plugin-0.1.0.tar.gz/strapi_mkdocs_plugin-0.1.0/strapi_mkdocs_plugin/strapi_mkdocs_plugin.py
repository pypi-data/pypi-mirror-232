"""Main module."""
"""Main module."""

import mkdocs # type: ignore
import requests

from mkdocs.plugins import BasePlugin 
from mkdocs.config import config_options 
from mkdocs.config import Config    


class StrapiPlugin(mkdocs.plugins.BasePlugin):
    config_scheme = ( 
        ("strapi_url", mkdocs.config.config_options.Type(str, required=True, default='a default value')),
        ("content_type", mkdocs.config.config_options.Type(str, required=True, default=None)),
    )

class StrapiPluginConfig(mkdocs.plugins.BasePlugin):
    strapi_url = mkdocs.config.config_options.Type(str, required=True, default='a default value')
    content_type = mkdocs.config.config_options.Type(str, required=True, default='a default value')
    
class StrapiPage(mkdocs.contrib.search.SearchPlugin):
    def on_config(self, config: Config, **kwargs) -> Config:
        """Add the StrapiPage to the markdown extensions."""
        config["markdown_extensions"].append("mkdocs_strapi_plugin.strapi_page")
        return config
    
    def on_page_content(self, html: str, page: mkdocs.structure.pages.Page, config: Config, files: mkdocs.structure.files.Files, **kwargs) -> str:
        """Add the StrapiPage to the markdown extensions."""
        if page.title == " ":
            return self.get_strapi_content()
        return html
    
    def get_strapi_content(self):
        r = requests.get('strapi_url')
        return r.json()
    
    def on_serve(self, server, config, **kwargs):
        """Add the StrapiPage to the markdown extensions."""
        server.watch('strapi_url', self.get_strapi_content)
        return config