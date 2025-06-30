from statistics import mean
from odoo import models, fields, api
from odoo.exceptions import UserError



class KPIReportGroup(models.Model):
    _name = 'kpi.report.group'
    _description = 'KPI Report Group'

    name = fields.Char(string='Report Name', required=True)
    description = fields.Text()
    kpi_ids = fields.One2many('kpi.report', 'report_id', string="KPIs")
    submission_ids = fields.One2many('kpi.report.submission', 'report_id', string="All Submissions")
    assigned_employee_ids = fields.Many2many('hr.employee', string="Assigned Employees")
    department = fields.Selection([
        ('sales', 'Sales'),
        ('operations', 'Operations'),
        ('marketing', 'Marketing'),
        ('finance', 'Finance'),
        ('hr', 'HR'),
        ('store', 'Store'),
        ('admin', 'Administration'),
        ('rnd', 'R&D'),
        ('it', 'IT')
    ], string='Department')
    
    group_submission_ids = fields.One2many(
                            'kpi.report.group.submission',
                            'report_id',
                            string="Group Submissions"
                        )
    
    score_label = fields.Char(string="Group Score Label", compute="_compute_score_label", store=True)
    score_color = fields.Selection([
        ('0', 'Grey'),
        ('1', 'Green'),    # Excellent
        ('2', 'Blue'),     # Good
        ('3', 'Orange'),   # Average
        ('4', 'Red'),      # Needs Improvement
        ('5', 'Darkred'),  # Underperformance
    ], string="Group Score Color", compute="_compute_score_label", store=True)


    def action_send_reminder_emails(self):
        template = self.env.ref('kpi_tracking.kpi_manual_entry_email_template', raise_if_not_found=False)

        if not template:
            raise UserError("Email template not found.")

        for rec in self:
            for kpi in rec.kpi_ids.filtered(lambda k: k.kpi_type == 'manual'):
                for user in kpi.assigned_user_ids:
                    if user.email:
                        template.with_context(kpi_name=kpi.name).send_mail(user.id, force_send=True)


    def action_refresh_all_kpis(self):
        for rec in self:
            for kpi in rec.kpi_ids:
                if kpi.kpi_type == 'manual':
                    kpi.sudo().action_manual_refresh_kpi()
                else:
                    kpi.sudo().scheduled_update_kpis()
  


    group_achievement_percent = fields.Float(
        string="Overall Target Achievement (%)",
        compute="_compute_group_achievement",
        store=True,
        digits=(16, 2)
    )

    @api.depends('kpi_ids.achievement_percent', 'kpi_ids.priority_weight')
    def _compute_group_achievement(self):
        for group in self:
            total_weight = 0.0
            weighted_score = 0.0

            for kpi in group.kpi_ids:
                weight = float(kpi.priority_weight or 1.0)
                capped_achievement = min(kpi.achievement_percent or 0.0, 100.0)  # Cap at 100%
                total_weight += weight
                weighted_score += capped_achievement * weight

            group.group_achievement_percent = (weighted_score / total_weight) if total_weight else 0.0

    @api.depends('group_achievement_percent')
    def _compute_score_label(self):
        for rec in self:
            percent = rec.group_achievement_percent or 0.0
            if percent >= 95:
                rec.score_label = "Excellent"
                rec.score_color = '1'
            elif percent >= 80:
                rec.score_label = "Good"
                rec.score_color = '2'
            elif percent >= 70:
                rec.score_label = "Average"
                rec.score_color = '3'
            elif percent >= 50:
                rec.score_label = "Needs Improvement"
                rec.score_color = '4'
            else:
                rec.score_label = "Underperformance"
                rec.score_color = '5'
