{
    'name': 'Employee Shift Report',
    'version': '1.0',
    'depends': ['base', 'hr'],
    'data': [
        'report/technician_report_template.xml',
        'views/report_action.xml',
        'views/employee_form_inherit.xml',
    ],
    'installable': True,
    'application': False,
}
