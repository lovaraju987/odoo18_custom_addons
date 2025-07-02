# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools

class TimesheetApprovalReport(models.Model):
    _name = 'timesheet.approval.report'
    _description = 'Timesheet Approval Analysis'
    _auto = False
    _rec_name = 'employee_id'

    # Dimensions
    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True)
    manager_id = fields.Many2one('hr.employee', string='Manager', readonly=True)
    project_id = fields.Many2one('project.project', string='Project', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    
    # Date fields
    date_from = fields.Date(string='Period Start', readonly=True)
    date_to = fields.Date(string='Period End', readonly=True)
    submission_date = fields.Datetime(string='Submission Date', readonly=True)
    approval_date = fields.Datetime(string='Approval Date', readonly=True)
    
    # State and status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Status', readonly=True)
    
    # Measures
    total_hours = fields.Float(string='Total Hours', readonly=True)
    approval_time_days = fields.Float(string='Approval Time (Days)', readonly=True)
    
    # Counts
    timesheet_count = fields.Integer(string='Timesheet Count', readonly=True)
    
    def init(self):
        """Initialize the report view"""
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    row_number() OVER () AS id,
                    ta.employee_id,
                    ta.manager_id,
                    ta.company_id,
                    ta.date_from,
                    ta.date_to,
                    ta.submission_date,
                    ta.approval_date,
                    ta.state,
                    ta.total_hours,
                    CASE 
                        WHEN ta.approval_date IS NOT NULL AND ta.submission_date IS NOT NULL 
                        THEN EXTRACT(epoch FROM (ta.approval_date - ta.submission_date)) / 86400.0
                        ELSE NULL 
                    END AS approval_time_days,
                    1 AS timesheet_count,
                    tal.project_id
                FROM timesheet_approval ta
                LEFT JOIN timesheet_approval_line tal ON ta.id = tal.approval_id
                WHERE ta.state != 'draft'
            )
        """ % self._table)
