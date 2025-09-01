# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError

class HrExpense(models.Model):
    _inherit = 'hr.expense'
    
    @api.model
    def create(self, vals):
        """Override create to ensure company and currency consistency"""
        if vals.get('employee_id'):
            employee = self.env['hr.employee'].browse(vals.get('employee_id'))
            if employee:
                # Set company from employee
                vals['company_id'] = employee.company_id.id
                # Set currency from employee's company
                vals['currency_id'] = employee.company_id.currency_id.id
        
        return super(HrExpense, self).create(vals)
    
    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        """Set company and currency when employee changes"""
        if self.employee_id:
            self.company_id = self.employee_id.company_id
            self.currency_id = self.employee_id.company_id.currency_id
    
    @api.constrains('company_id', 'product_id')
    def _check_product_company(self):
        """Ensure expense category belongs to employee's company or is shared"""
        for expense in self:
            if expense.product_id and expense.product_id.company_id and expense.product_id.company_id != expense.company_id:
                raise ValidationError(_("The expense category must belong to the same company as the expense or be shared across companies."))

class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'
    
    @api.model
    def create(self, vals):
        """Override create to ensure company and currency consistency for sheets"""
        if vals.get('employee_id'):
            employee = self.env['hr.employee'].browse(vals.get('employee_id'))
            if employee:
                # Set company from employee
                vals['company_id'] = employee.company_id.id
                # Set currency from employee's company
                vals['currency_id'] = employee.company_id.currency_id.id
        
        return super(HrExpenseSheet, self).create(vals)
    
    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        """Set company and currency when employee changes"""
        if self.employee_id:
            self.company_id = self.employee_id.company_id
            self.currency_id = self.employee_id.company_id.currency_id
    
    @api.constrains('expense_line_ids', 'company_id')
    def _check_expense_lines_company(self):
        """Ensure all expenses in sheet belong to same company as the sheet"""
        for sheet in self:
            expenses_company = sheet.expense_line_ids.mapped('company_id')
            if len(expenses_company) > 1 or (expenses_company and expenses_company != sheet.company_id):
                raise ValidationError(_("All expenses in an expense report must belong to the same company."))
