{
    'name': 'TechCarrot CRM Customization',
    'version': '18.0.1.0.0',
    'category': 'Customer Relationship Management',
    'summary': 'Custom fields for CRM module',
    'description': """
        This module adds custom fields to the CRM module:
        - Point of contact (links to contacts)
        - Practice (many-to-one field linked to practice master)
        - Deal manager (links to employee records)
        - Proposal submission date (date field)
        - Engaged Presales (checkbox)
        - Industry (many-to-one field linked to industry master)
    """,
    'author': 'TechCarrot',
    'website': 'https://www.techcarrot.com',
    'depends': ['crm', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'data/crm_practice_data.xml',
        'data/crm_industry_data.xml',
        'data/crm_lead_type_data.xml',
        'views/crm_practice_views.xml',
        'views/crm_industry_views.xml',
        'views/crm_lead_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
