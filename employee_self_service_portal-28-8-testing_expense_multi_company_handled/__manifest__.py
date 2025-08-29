# __manifest__.py
{
    "name": "Employee Self Service Portal MLR",
    "version": "18.1.5",
    "depends": ["portal", "hr", "hr_attendance", "hr_payroll", "hr_holidays", "hr_expense", "techcarrot_crm_mlr"],
    "category": "Human Resources",
    "author": "Lovaraju Mylapalli",
    "website": "https://www.mlr.com",
    "description": """
        Employee Self Service Portal MLR
        =================================
        This module provides a portal for employees to manage their personal information, attendance, and other HR-related tasks. this is techcarrot customized
    """,
    "images": ["static/description/banner.png"],
    "summary": "Allow employees to access and manage their information via portal access.",
    "data": [
        "security/portal_access_groups.xml",  # Must be loaded first to create groups
        "security/ir.model.access.csv",
        "security/portal_employee_security.xml",
        "data/portal_data.xml",
        "data/attendance_cron.xml",  # Auto-checkout cron job
        "data/expense_categories.xml",  # Default expense categories
        "views/menu.xml",
        "views/portal_layout.xml",
        "views/portal_ess_dashboard.xml",
        "views/portal_ess_dashboard_enhanced.xml",
        "views/Employee_details/portal_employee_templates.xml",
        "views/Employee_details/portal_attendance_templates.xml",
        "views/Employee_details/employee_form_view.xml",
        "views/Employee_details/portal_employee_edit_templates.xml",
        "views/Employee_details/portal_employee_profile_personal.xml",
        "views/Employee_details/portal_employee_profile_experience.xml",
        "views/Employee_details/portal_employee_profile_certification.xml",
        "views/Employee_details/portal_employee_profile_bank.xml",
        "views/Employee_details/portal_employee_profile_base.xml",
        "views/Employee_details/portal_employee_crm.xml",  # CRM portal template
        "views/Employee_details/portal_employee_crm_enhanced.xml",  # Enhanced CRM template
        "views/Employee_details/portal_employee_crm_create.xml",  # CRM create form
        "views/Employee_details/portal_employee_crm_edit.xml",    # CRM edit form
        "views/Employee_details/portal_employee_crm_activity_edit.xml",  # Activity edit form for CRM
        "views/Employee_details/portal_employee_crm_activity_modal.xml",  # Activity modal templates
        "views/Employee_details/portal_employee_crm_notes_modal.xml",  # Notes modal template
        "views/Employee_details/portal_expense_templates.xml",
        "views/Employee_details/portal_expense_submit.xml",  # New expense submission template
        "views/Employee_details/portal_payslip_templates.xml",  # Payslip templates
        "views/Employee_details/portal_payslip_view.xml",  # Payslip detail view
    ],
    "installable": True,
    "application": True,
    "license": "LGPL-3"
}