# -*- coding: utf-8 -*-

import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def post_install_hook(cr, registry):
    """Post-install hook to setup timesheet approval module"""
    
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        
        _logger.info("Running timesheet approval post-install setup...")
        
        try:
            # 1. Ensure timesheet approval groups are properly assigned
            user_group = env.ref('timesheet_approval.group_timesheet_approval_user', raise_if_not_found=False)
            manager_group = env.ref('timesheet_approval.group_timesheet_approval_manager', raise_if_not_found=False)
            
            if user_group:
                # Add user group to all users with employee records
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
            
            if manager_group:
                # Add manager group to users who manage employees
                for user in env['res.users'].search([('employee_id', '!=', False), ('active', '=', True)]):
                    if user.employee_id and user.employee_id.child_ids:
                        if manager_group not in user.groups_id:
                            _logger.info(f"Adding manager group to user {user.name}")
                            user.groups_id = [(4, manager_group.id)]
            
            # 2. Setup default configuration parameters if they don't exist
            params = env['ir.config_parameter'].sudo()
            
            default_configs = {
                'timesheet_approval.submission_deadline_days': '7',
                'timesheet_approval.approval_deadline_days': '3',
                'timesheet_approval.email_submission_enabled': 'True',
                'timesheet_approval.email_approval_enabled': 'True',
                'timesheet_approval.email_reminder_enabled': 'True',
                'timesheet_approval.reminder_frequency_days': '2',
                'timesheet_approval.batch_approval_limit': '50',
                'timesheet_approval.project_allocation_integration': 'True',
                'timesheet_approval.allow_draft_editing': 'True',
                'timesheet_approval.standard_hours_threshold': '8.0',
            }
            
            for key, default_value in default_configs.items():
                if not params.get_param(key):
                    params.set_param(key, default_value)
                    _logger.info(f"Set default config parameter: {key} = {default_value}")
            
            # 3. Recompute manager_id for any existing timesheet approvals
            approvals = env['timesheet.approval'].search([])
            if approvals:
                _logger.info(f"Recomputing manager_id for {len(approvals)} existing timesheet approvals")
                approvals._compute_manager_id()
            
            _logger.info("Timesheet approval post-install setup completed successfully")
            
        except Exception as e:
            _logger.error(f"Error during timesheet approval post-install setup: {e}")
            # Don't raise the error to prevent installation failure


def uninstall_hook(cr, registry):
    """Uninstall hook to cleanup timesheet approval module data"""
    
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        
        _logger.info("Running timesheet approval uninstall cleanup...")
        
        try:
            # Remove configuration parameters
            params = env['ir.config_parameter'].sudo()
            config_keys = [
                'timesheet_approval.submission_deadline_days',
                'timesheet_approval.approval_deadline_days',
                'timesheet_approval.auto_submission_enabled',
                'timesheet_approval.email_submission_enabled',
                'timesheet_approval.email_approval_enabled',
                'timesheet_approval.email_reminder_enabled',
                'timesheet_approval.reminder_frequency_days',
                'timesheet_approval.require_manager_comments',
                'timesheet_approval.allow_self_approval',
                'timesheet_approval.batch_approval_limit',
                'timesheet_approval.project_allocation_integration',
                'timesheet_approval.portal_access_enabled',
                'timesheet_approval.allow_draft_editing',
                'timesheet_approval.auto_approve_standard_hours',
                'timesheet_approval.standard_hours_threshold',
            ]
            
            for key in config_keys:
                param = env['ir.config_parameter'].search([('key', '=', key)])
                if param:
                    param.unlink()
                    _logger.info(f"Removed config parameter: {key}")
            
            _logger.info("Timesheet approval uninstall cleanup completed")
            
        except Exception as e:
            _logger.error(f"Error during timesheet approval uninstall cleanup: {e}")
            # Don't raise the error to prevent uninstall failure
