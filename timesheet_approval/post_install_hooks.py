#!/usr/bin/env python3
"""
Module upgrade script for timesheet approval
This script should be run after upgrading the module to ensure all data is properly updated
"""

def post_install_hook(cr, registry):
    """Post-install hook to update existing data"""
    import logging
    from odoo import api, SUPERUSER_ID
    
    _logger = logging.getLogger(__name__)
    
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        
        _logger.info("Running timesheet approval post-install updates...")
        
        # 1. Recompute manager_id for all existing timesheet approvals
        approvals = env['timesheet.approval'].search([])
        if approvals:
            _logger.info(f"Recomputing manager_id for {len(approvals)} timesheet approvals")
            approvals._compute_manager_id()
        
        # 2. Recompute can_approve_ui for all existing records
        if approvals:
            _logger.info(f"Computing can_approve_ui for {len(approvals)} timesheet approvals")
            approvals._compute_can_approve_ui()
        
        # 3. Ensure timesheet approval groups are properly assigned
        # Add user group to all users with employee records
        user_group = env.ref('timesheet_approval.group_timesheet_approval_user')
        users_with_employees = env['res.users'].search([
            ('employee_id', '!=', False),
            ('active', '=', True)
        ])
        
        users_to_update = users_with_employees.filtered(
            lambda u: user_group not in u.groups_id
        )
        
        if users_to_update:
            _logger.info(f"Adding user group to {len(users_to_update)} users")
            for user in users_to_update:
                user.groups_id = [(4, user_group.id)]
        
        # Add manager group to users who manage employees
        manager_group = env.ref('timesheet_approval.group_timesheet_approval_manager')
        
        for user in users_with_employees:
            if user.employee_id:
                direct_reports = env['hr.employee'].search([
                    ('parent_id', '=', user.employee_id.id)
                ])
                
                if direct_reports and manager_group not in user.groups_id:
                    _logger.info(f"Adding manager group to {user.name} (manages {len(direct_reports)} employees)")
                    user.groups_id = [(4, manager_group.id)]
        
        _logger.info("Timesheet approval post-install updates completed")

def uninstall_hook(cr, registry):
    """Clean up when module is uninstalled"""
    import logging
    from odoo import api, SUPERUSER_ID
    
    _logger = logging.getLogger(__name__)
    _logger.info("Timesheet approval module uninstall cleanup completed")
