# -*- coding: utf-8 -*-
{
    'name': "api_sales_orders",

    'summary': "API for Sales Orders",

    'description': """
    Long description of module's purpose
    This module provides an API for managing sales orders in Odoo.
    It includes endpoints for creating, updating, and retrieving sales orders.
    The API is designed to be secure and efficient, allowing for easy integration with other systems.
    Features:
        - Create, update, and retrieve sales orders
        - Secure API access with API keys
        - Role-based access control for different user roles
        - Detailed logging of API access for monitoring and auditing
        - Support for filtering and sorting sales orders based on various criteria
        - Easy integration with third-party applications and services
        - Comprehensive documentation for developers
        - Support for multiple authentication methods
        - Rate limiting to prevent abuse and ensure fair usage
        - Error handling and validation for robust API interactions
    """,

    'author': "Lovaraju",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Technical',
    'version': '18.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'api_management'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}

