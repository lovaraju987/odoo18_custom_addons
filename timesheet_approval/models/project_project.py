# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProjectProject(models.Model):
    _inherit = 'project.project'

    # Timesheet Approval Settings
    timesheet_approval_required = fields.Boolean(
        string='Timesheet Approval Required',
        default=True,
        help="Whether timesheets for this project require approval"
    )
    
    timesheet_approver_ids = fields.Many2many(
        'hr.employee',
        'project_timesheet_approver_rel',
        'project_id',
        'employee_id',
        string='Timesheet Approvers',
        help="Additional employees who can approve timesheets for this project"
    )
    
    # Statistics
    pending_timesheet_approvals = fields.Integer(
        string='Pending Approvals',
        compute='_compute_timesheet_approval_stats',
        help="Number of pending timesheet approvals for this project"
    )
    
    total_timesheet_approvals = fields.Integer(
        string='Total Approvals',
        compute='_compute_timesheet_approval_stats',
        help="Total number of timesheet approvals for this project"
    )
    
    approved_hours_this_month = fields.Float(
        string='Approved Hours (This Month)',
        compute='_compute_timesheet_approval_stats',
        help="Total approved hours for this project this month"
    )
    
    @api.depends('task_ids.timesheet_ids')
    def _compute_timesheet_approval_stats(self):
        """Compute timesheet approval statistics"""
        for project in self:
            # Get all timesheet approval lines for this project
            approval_lines = self.env['timesheet.approval.line'].search([
                ('project_id', '=', project.id)
            ])
            
            # Count pending approvals
            pending = approval_lines.filtered(
                lambda l: l.approval_id.state == 'submitted'
            )
            project.pending_timesheet_approvals = len(set(pending.mapped('approval_id.id')))
            
            # Count total approvals
            project.total_timesheet_approvals = len(set(approval_lines.mapped('approval_id.id')))
            
            # Calculate approved hours this month
            from datetime import date
            current_month_start = date.today().replace(day=1)
            
            approved_lines = approval_lines.filtered(
                lambda l: l.approval_id.state == 'approved' and
                l.approval_id.approval_date and
                l.approval_id.approval_date.date() >= current_month_start
            )
            project.approved_hours_this_month = sum(approved_lines.mapped('unit_amount'))
    
    def action_view_timesheet_approvals(self):
        """Action to view timesheet approvals for this project"""
        self.ensure_one()
        
        # Get all approval IDs that have lines for this project
        approval_lines = self.env['timesheet.approval.line'].search([
            ('project_id', '=', self.id)
        ])
        approval_ids = approval_lines.mapped('approval_id.id')
        
        action = self.env.ref('timesheet_approval.action_timesheet_approval_manager').read()[0]
        action['domain'] = [('id', 'in', approval_ids)]
        action['context'] = {
            'search_default_project_id': self.id,
        }
        
        return action
    
    def action_view_pending_approvals(self):
        """Action to view pending timesheet approvals for this project"""
        self.ensure_one()
        
        # Get pending approval IDs for this project
        approval_lines = self.env['timesheet.approval.line'].search([
            ('project_id', '=', self.id),
            ('approval_id.state', '=', 'submitted')
        ])
        approval_ids = approval_lines.mapped('approval_id.id')
        
        action = self.env.ref('timesheet_approval.action_timesheet_approval_manager').read()[0]
        action['domain'] = [('id', 'in', approval_ids), ('state', '=', 'submitted')]
        action['context'] = {
            'search_default_submitted': 1,
        }
        
        return action
    
    def can_approve_timesheets(self, user=None):
        """Check if user can approve timesheets for this project"""
        if user is None:
            user = self.env.user
        
        # Project manager can approve
        if self.user_id == user:
            return True
        
        # Additional approvers can approve
        if user.employee_id and user.employee_id in self.timesheet_approver_ids:
            return True
        
        # HR managers can approve
        if user.has_group('hr.group_hr_manager'):
            return True
        
        # System admin can approve
        if user.has_group('base.group_system'):
            return True
        
        return False
