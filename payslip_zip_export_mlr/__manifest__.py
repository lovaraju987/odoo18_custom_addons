{
    'name': 'Payslip ZIP Export MLR',
    'version': '1.0',
    'odoo_version': '18.0',
    'summary': 'Export multiple payslips as a ZIP archive',
    'category': 'Human Resources',
    'author': 'Lovaraju Mylapalli',
    'depends': ['om_hr_payroll'],
    'data': [
        'views/payslip_zip_export_wizard_view.xml',
        'views/hr_payslip_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}