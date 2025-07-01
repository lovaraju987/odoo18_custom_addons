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
    
    allocated_hours = fields.Float(
        string="Allocated Hours",
        compute="_compute_allocated_hours",
        help="Total hours allocated to this employee based on allocation percentage",
        store=False
    )
    
    @api.depends('allocation_percentage', 'project_id.allocated_hours')
    def _compute_allocated_hours(self):
        for record in self:
            if record.allocation_percentage and record.project_id.allocated_hours:
                record.allocated_hours = (record.allocation_percentage / 100.0) * record.project_id.allocated_hours
            else:
                record.allocated_hours = 0.0

    @api.model
    def create(self, vals):
        """Override create to auto-distribute percentages when new employee is added"""
        record = super().create(vals)
        if record.project_id:
            self._auto_distribute_percentages(record.project_id)
        return record

    def unlink(self):
        """Override unlink to auto-distribute percentages when employee is removed"""
        projects = self.mapped('project_id')
        result = super().unlink()
        for project in projects:
            self._auto_distribute_percentages(project)
        return result

    def _auto_distribute_percentages(self, project):
        """Automatically distribute equal percentages among all employees in a project"""
        if not project:
            return
            
        # Get all allocation records for this project
        all_allocations = self.search([('project_id', '=', project.id)])
        
        if not all_allocations:
            return
            
        # Calculate equal percentage for each employee
        equal_percentage = 100.0 / len(all_allocations)
        
        # Update all allocations with equal percentage
        for allocation in all_allocations:
            allocation.allocation_percentage = equal_percentage

    @api.constrains('allocation_percentage')
    def _check_total_allocation_percentage(self):
        """Ensure total allocation percentage for a project doesn't exceed 100%"""
        for record in self:
            if not record.project_id:
                continue
            
            # Get all allocation records for this project
            all_allocations = self.search([('project_id', '=', record.project_id.id)])
            total_percentage = sum(all_allocations.mapped('allocation_percentage'))
            
            if total_percentage > 100.0:
                raise exceptions.ValidationError(
                    f"Total allocation percentage for project '{record.project_id.name}' "
                    f"cannot exceed 100%. Current total: {total_percentage:.1f}%"
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
