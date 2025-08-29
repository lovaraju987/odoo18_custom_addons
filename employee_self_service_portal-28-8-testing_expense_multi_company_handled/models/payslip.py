# models/payslip.py
from odoo import models, fields, api


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def get_portal_payslips_count(self, employee_id):
        """Get count of payslips for an employee for portal display"""
        return self.search_count([('employee_id', '=', employee_id)])

    @api.model
    def get_latest_payslip(self, employee_id):
        """Get latest payslip for an employee"""
        return self.search([
            ('employee_id', '=', employee_id),
            ('state', 'in', ['done', 'paid'])
        ], order='date_from desc', limit=1)
        
    def can_employee_download(self):
        """Check if employee can download this payslip"""
        self.ensure_one()
        return self.state in ['done', 'paid']
        
    def get_formatted_period(self):
        """Get formatted period string for display"""
        self.ensure_one()
        if self.date_from and self.date_to:
            return f"{self.date_from.strftime('%B %Y')}"
        return "N/A"
        
    def get_payslip_summary(self):
        """Get summary data for portal display"""
        self.ensure_one()
        earnings = sum(line.total for line in self.line_ids.filtered(lambda l: l.total > 0))
        deductions = sum(abs(line.total) for line in self.line_ids.filtered(lambda l: l.total < 0))
        
        return {
            'earnings': earnings,
            'deductions': deductions,
            'net_pay': self.net_wage or 0.0,
            'gross_pay': self.basic_wage or 0.0,
        }
