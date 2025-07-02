# -*- coding: utf-8 -*-
{
    'name': 'Timesheet Approval Workflow',
    'version': '18.0.1.0.0',
    'category': 'Human Resources/Timesheets',
    'summary': 'Complete timesheet approval workflow system for Odoo Community Edition',
    'description': """
        Timesheet Approval Workflow
        ===========================
        
        This module provides a comprehensive timesheet approval workflow system designed 
        specifically for Odoo Community Edition. It seamlessly integrates with existing 
        timesheet and project allocation systems.
        
        Key Features:
        -------------
        * Timesheet submission workflow with multiple states
        * Manager approval system with comments and history
        * Batch approval operations for efficiency
        * Email notifications for submissions and approvals
        * Complete audit trail and approval history
        * Integration with employee project allocation module
        * Flexible approval hierarchy and delegation
        * Dashboard views for managers and employees
        * Advanced filtering and search capabilities
        * Mobile-friendly interface for approval on-the-go
        
        Workflow States:
        ---------------
        * Draft: Employee can edit timesheet entries
        * Submitted: Awaiting manager approval
        * Approved: Approved by manager, locked for editing
        * Rejected: Rejected by manager with comments, back to draft
        
        Integration:
        -----------
        * Works seamlessly with employee_project_allocation module
        * Maintains all existing timesheet functionality
        * Respects project allocation limits and validation rules
        * Provides approval controls without disrupting existing workflows
    """,
    'author': 'OneTo7 Services',
    'website': 'https://www.oneto7.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'hr',
        'hr_timesheet', 
        'project',
        'mail',
        'portal',
        'employee_project_allocation',
    ],
    'data': [
        'security/timesheet_approval_security.xml',
        'security/ir.model.access.csv',
        'data/mail_template_data.xml',
        'data/ir_cron_data.xml',
        'views/timesheet_approval_views.xml',
        'views/timesheet_approval_manager_views.xml',
        'views/timesheet_approval_employee_views.xml',
        'views/timesheet_approval_dashboard_views.xml',
        'views/timesheet_approval_settings_views.xml',
        'views/timesheet_approval_menus.xml',
        'wizard/timesheet_batch_approval_views.xml',
        'wizard/timesheet_submission_views.xml',
        'wizard/timesheet_submission_wizard_simple_views.xml',
        'reports/timesheet_approval_reports.xml',
    ],
    'demo': [
        'demo/demo_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'timesheet_approval/static/src/css/timesheet_approval.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'post_init_hook': 'post_install_hook',
    'uninstall_hook': 'uninstall_hook',
    'external_dependencies': {
        'python': [],
    },
}
