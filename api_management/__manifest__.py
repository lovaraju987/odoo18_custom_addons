# -*- coding: utf-8 -*-
{
    "name": "API Management Base",
    "version": "18.0",
    "category": "Technical",
    "summary": "Reusable module to manage API keys and access logs",
    "description": """
        This module provides a base structure for managing API keys and access logs.
        It includes models for API keys, access logs, and a dashboard for monitoring API usage.
    """,
    "author": "Lovaraju",
    "maintainer": "Lovaraju",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_api_endpoint_wizard_views.xml",
        "views/res_api_key_views.xml",
        "views/res_api_endpoint_views.xml",
        "views/api_access_log_views.xml",
        "views/api_dashboard_views.xml",
        # "views/menu.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
