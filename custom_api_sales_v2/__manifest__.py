{
    "name": "Custom Sales API V2",
    "version": "18.7",
    "description": "Custom API for Sales Orders with enhanced security, dashboard and logging. "
    "Features: include API key management, access logging, role-based access control, Key Regenerate button and field filtering.",
    "summary": "Custom API for Sales Orders with enhanced security and logging.",
    "author": "Lovaraju Mylapalli",
    "category": "Tools",
    "depends": ["base", "sale"],
    "data": [
            'security/ir.model.access.csv',
            'views/res_api_key_views.xml',
            'views/api_access_log_views.xml',
            'views/api_dashboard_views.xml',
            # 'views/menu.xml',
    ],
    "installable": True,
    "application": False
}
