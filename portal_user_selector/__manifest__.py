{
    'name': 'Portal User Selector',
    'version': '1.0',
    'summary': 'Allow portal users to be selectable in user fields like CRM Salesperson and Project Assignee',
    'description': 'Removes default internal-user-only domain in CRM and Project modules so portal users can be assigned.',
    'category': 'Tools',
    'author': 'Techcarrot',
    'depends': ['crm', 'project'],
    'data': [
        'views/user_selector_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
