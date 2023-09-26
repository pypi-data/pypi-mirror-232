=====
Usage
=====

To use mkdocs_strapi_plugin in a project::

    import mkdocs_strapi_plugin as strapi

    plugins = [
        strapi.StrapiPlugin()
    ]   

Configuration
=============
The plugin can be configured in the `mkdocs.yml` file:

    plugins:
        - strapi:
            url: http://localhost:1337
            content_types:
                - articles
                - categories