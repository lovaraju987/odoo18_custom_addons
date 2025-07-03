# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError

class TimesheetBatchApproval(models.TransientModel):
    _name = 'timesheet.batch.approval'
    _description = 'Batch Timesheet Approval Wizard'

    # Selection Options
    approval_action = fields.Selection([
        ('approve', 'Approve Selected'),
        ('reject', 'Reject Selected'),
    ], string='Action', required=True, default='approve',
       help="Action to perform on selected timesheets")
    
    # Comments
    comments = fields.Text(
        string='Comments',
        help="Comments for the approval/rejection (required for rejection)"
    )
    
    # Selected Timesheets
    timesheet_approval_ids = fields.Many2many(
        'timesheet.approval',
        string='Timesheet Approvals',
        help="Timesheets to process"
    )
    
    # Summary Information
    total_timesheets = fields.Integer(
        string='Total Timesheets',
        compute='_compute_summary',
        help="Total number of selected timesheets"
    )
    
    total_hours = fields.Float(
        string='Total Hours',
        compute='_compute_summary',
        help="Total hours across all selected timesheets"
    )
    
    employees_count = fields.Integer(
        string='Employees Count',
        compute='_compute_summary',
        help="Number of unique employees"
    )
    
    projects_count = fields.Integer(
        string='Projects Count',
        compute='_compute_summary',
        help="Number of unique projects"
    )
    
    @api.depends('timesheet_approval_ids')
    def _compute_summary(self):
        """Compute summary information"""
        for wizard in self:
            timesheets = wizard.timesheet_approval_ids
            wizard.total_timesheets = len(timesheets)
            wizard.total_hours = sum(timesheets.mapped('total_hours'))
            wizard.employees_count = len(set(timesheets.mapped('employee_id.id')))
            
            # Count unique projects across all timesheet lines
            all_project_ids = set()
            for timesheet in timesheets:
                all_project_ids.update(timesheet.timesheet_line_ids.mapped('project_id.id'))
            wizard.projects_count = len(all_project_ids)
    
    @api.constrains('approval_action', 'comments')
    def _check_rejection_comments(self):
        """Ensure comments are provided for rejections"""
        for wizard in self:
            if wizard.approval_action == 'reject' and not wizard.comments:
                raise exceptions.ValidationError(_("Comments are required when rejecting timesheets."))
    
    def action_process_timesheets(self):
        """Process the selected timesheets"""
        self.ensure_one()
        
        if not self.timesheet_approval_ids:
            raise UserError(_("No timesheets selected for processing."))
        
        # Check batch limit configuration
        settings = self.env['timesheet.approval.settings']
        batch_limit = settings.get_config_value('batch_approval_limit', 50)
        
        if len(self.timesheet_approval_ids) > batch_limit:
            raise UserError(_(
                "Batch limit exceeded. You can process maximum %d timesheets at once. "
                "Current selection: %d timesheets. Please reduce your selection or contact administrator to increase the limit."
            ) % (batch_limit, len(self.timesheet_approval_ids)))
        
        # Validate timesheets can be processed
        valid_timesheets = self.timesheet_approval_ids.filtered(lambda t: t.state == 'submitted')
        
        if not valid_timesheets:
            raise UserError(_("No submitted timesheets found. Only submitted timesheets can be approved/rejected."))
        
        invalid_count = len(self.timesheet_approval_ids) - len(valid_timesheets)
        if invalid_count > 0:
            # Show warning but continue with valid ones
            self.env.user.notify_warning(
                message=_("%d timesheet(s) were skipped as they are not in submitted state.") % invalid_count
            )
        
        # Check permissions
        for timesheet in valid_timesheets:
            if not timesheet._can_approve():
                raise UserError(_(
                    "You don't have permission to approve timesheet for %s."
                ) % timesheet.employee_id.name)
        
        # Check if comments are required based on configuration
        require_comments = settings.get_config_value('require_manager_comments', False)
        if require_comments and not self.comments:
            raise UserError(_("Manager comments are required for batch approval/rejection. Please provide comments."))
        
        # Process timesheets
        processed_count = 0
        errors = []
        
        for timesheet in valid_timesheets:
            try:
                if self.approval_action == 'approve':
                    timesheet.approval_comments = self.comments
                    timesheet.action_approve()
                else:  # reject
                    timesheet.approval_comments = self.comments
                    timesheet.action_reject()
                
                processed_count += 1
                
            except Exception as e:
                errors.append(f"{timesheet.employee_id.name}: {str(e)}")
        
        # Prepare result message
        if self.approval_action == 'approve':
            action_msg = "approved"
        else:
            action_msg = "rejected"
        
        success_msg = _("%d timesheet(s) successfully %s.") % (processed_count, action_msg)
        
        if errors:
            error_msg = _("Errors occurred for:\n%s") % "\n".join(errors)
            message = f"{success_msg}\n\n{error_msg}"
        else:
            message = success_msg
        
        # Return action with message
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Batch Processing Complete'),
                'message': message,
                'type': 'success' if not errors else 'warning',
                'sticky': True,
            }
        }
    
    @api.model
    def default_get(self, fields_list):
        """Set default values from context"""
        res = super().default_get(fields_list)
        
        # Get selected timesheets from context
        active_ids = self.env.context.get('active_ids', [])
        if active_ids:
            res['timesheet_approval_ids'] = [(6, 0, active_ids)]
        
        return res
    
    def action_preview_timesheets(self):
        """Preview selected timesheets before processing"""
        self.ensure_one()
        
        action = self.env.ref('timesheet_approval.action_timesheet_approval_manager').read()[0]
        action['domain'] = [('id', 'in', self.timesheet_approval_ids.ids)]
        action['context'] = {
            'search_default_submitted': 1,
        }
        
        return action
