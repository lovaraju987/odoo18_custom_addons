{
    'name': 'Real Estate Management MLR',
    'version': '18.0.1.0.0',
    'category': 'Real Estate',
    'summary': 'Manage regions, projects, properties, and units',
    'description': """\
Real Estate Management Module
Phase 1 implements core models for regions, projects, properties, and units.
""",
    'author': 'Your Company Name',
    'website': 'https://yourcompany.example.com',
    'depends': ['base', 'stock'],
    'data': [
        'security/realestate_security.xml',
        'security/ir.model.access.csv',
        'views/region_views.xml',
        'views/project_views.xml',
        'views/property_views.xml',
        'views/unit_views.xml',
        'views/realestate_menus.xml',
        'views/dashboard_views.xml',
        'views/unit_create_wizard_views.xml',
        'views/furniture_views.xml',
        'views/furniture_transfer_wizard_views.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
