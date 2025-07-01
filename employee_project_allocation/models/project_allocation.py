# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions

# Extend the existing Sale Line Employee Map to add allocation percentage
class ProjectSaleLineEmployeeMap(models.Model):
    _inherit = "project.sale.line.employee.map"

    allocation_percentage = fields.Float(
        string="Allocation %",
        help="What % of this project is allocated to this employee?",
        default=0.0
    )

# Extend Timesheet Line to enforce allocation and daily hour limits
class TimesheetLine(models.Model):
    _inherit = "account.analytic.line"

    @api.constrains('unit_amount')
    def _check_project_allocation_limit(self):
        for line in self:
            if not line.project_id or not line.employee_id:
                continue

            project = line.project_id
            emp = line.employee_id

            # Step 1: Check if the employee has an allocation on this project
            allocation = project.sale_line_employee_ids.filtered(
                lambda l, emp=emp: l.employee_id == emp and l.allocation_percentage > 0.0
            )
            
            if not allocation:
                continue  # No restriction if no allocation set

            allocated_hours = project.allocated_hours or 0.0
            max_allowed = allocated_hours * (allocation[0].allocation_percentage / 100.0)

            # Step 2: Calculate total hours already logged on this project
            total_logged = sum(line.search([
                ('employee_id', '=', emp.id),
                ('project_id', '=', project.id),
                ('id', '!=', line.id)  # exclude current line during update
            ]).mapped('unit_amount')) + line.unit_amount

            if total_logged > max_allowed:
                raise exceptions.ValidationError(
                    f"{emp.name} is allowed to log only {allocation[0].allocation_percentage}% "
                    f"({max_allowed:.2f} hrs) on project '{project.name}'. Already logged: {total_logged:.2f} hrs."
                )

    @api.constrains('date', 'employee_id', 'unit_amount')
    def _check_daily_limit(self):
        for line in self:
            if not line.date or not line.employee_id:
                continue

            DAILY_LIMIT = 9.0  # can be made configurable in settings

            # Total hours on same day
            total_today = sum(self.search([
                ('employee_id', '=', line.employee_id.id),
                ('date', '=', line.date),
                ('id', '!=', line.id)
            ]).mapped('unit_amount')) + line.unit_amount

            if total_today > DAILY_LIMIT:
                raise exceptions.ValidationError(
                    f"{line.employee_id.name} cannot log more than {DAILY_LIMIT} hours on {line.date}. "
                    f"Attempted: {total_today:.2f} hrs."
                )
