# -*- coding: utf-8 -*-
{
    'name': 'Portal Leads Management | Website Portal Leads',
    'description': """
          Lead Portal - Website
    """,
    'summary': 'Lead Portal - Website',
    'version': '1.0',
    'category': 'Website',
    'author': 'TechKhedut Inc.',
    'company': 'TechKhedut Inc.',
    'maintainer': 'TechKhedut Inc.',
    'website': "https://www.techkhedut.com",
    'depends': [
        'crm',
        'portal',
        'website',
        'sale',
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',
        # Views
        'views/portal_leads_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            "tk_portal_partner_leads/static/src/js/script.js",
        ],
    },
    'images': ['static/description/banner.png'],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
