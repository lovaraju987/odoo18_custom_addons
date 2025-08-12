# __manifest__.py
{
    "name": "Employee Self Service Portal MLR",
    "version": "18.1.6",  # Enhanced Leave Requests with JavaScript utilities
    "depends": ["portal", "hr", "hr_attendance", "om_hr_payroll", "hr_holidays"],
    "category": "Human Resources",
    "author": "Lovaraju Mylapalli",
    "website": "https://www.mlr.com",
    "description": """
        Employee Self Service Portal MLR
        =================================
        This module provides a portal for employees to manage their personal information, attendance, CRM activities, expenses, payslips, and leave requests through the portal interface.
        
        Features:
        - Personal Profile Management
        - Attendance Tracking with GPS
        - CRM Lead Management
        - Expense Management
        - Payslip Viewing and Download
        - Leave Request Management
        - Comprehensive Filtering and Search
    """,
    "images": ["static/description/banner.png"],
    "summary": "Allow employees to access and manage their information via portal access.",
    "data": [
        "security/ir.model.access.csv",
        "security/portal_employee_security.xml",
        "data/portal_data.xml",
        "views/menu.xml",
        "views/portal_layout.xml",
        "views/portal_ess_dashboard.xml",
        "views/employee_details/portal_employee_templates.xml",
        "views/employee_details/portal_attendance_templates.xml",
        "views/employee_details/employee_form_view.xml",
        "views/employee_details/portal_employee_edit_templates.xml",
        "views/employee_details/portal_employee_profile_personal.xml",
        "views/employee_details/portal_employee_profile_experience.xml",
        "views/employee_details/portal_employee_profile_certification.xml",
        "views/employee_details/portal_employee_profile_bank.xml",
        "views/employee_details/portal_employee_profile_base.xml",
        "views/employee_details/portal_employee_crm.xml",  # CRM portal template
        "views/employee_details/portal_employee_crm_create.xml",  # CRM create form
        "views/employee_details/portal_employee_crm_edit.xml",    # CRM edit form
        "views/employee_details/portal_employee_crm_activity_edit.xml",  # Activity edit form for CRM
        "views/employee_details/portal_expense_templates.xml",
        "views/employee_details/portal_expense_submit.xml",  # New expense submission template
        "views/employee_details/portal_payslips_templates.xml",  # Payslips templates
        "views/employee_details/portal_leaves_templates.xml",    # Leave requests templates
    ],
    "assets": {
        "web.assets_frontend": [
            "employee_self_service_portal/static/src/css/portal_style.css",
            "employee_self_service_portal/static/src/js/portal_utils.js",
            "employee_self_service_portal/static/src/js/leave_form.js",
        ],
    },
    "installable": True,
    "application": True,
    "license": "LGPL-3"
}