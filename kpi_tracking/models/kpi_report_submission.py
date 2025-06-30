from odoo import models, fields, api

class KPIReportSubmission(models.Model):
    _name = 'kpi.report.submission'
    _description = 'KPI Report Submission'
    _order = 'date desc'

    report_id = fields.Many2one('kpi.report.group', string="Report Group", related='kpi_id.report_id', store=True)
    kpi_id = fields.Many2one('kpi.report', string="KPI", required=True)
    kpi_type = fields.Selection(related='kpi_id.kpi_type', store=True)
    report_type = fields.Selection(related='kpi_id.report_type', store=True)
    department = fields.Selection(related='kpi_id.department', store=True)
    target_type = fields.Selection(related='kpi_id.target_type', store=True)
    target_value = fields.Float(related='kpi_id.target_value', store=True)
    target_unit_display = fields.Char(related='kpi_id.target_unit_display', store=True)
    kpi_direction = fields.Selection(related='kpi_id.kpi_direction', store=True)
    priority_weight = fields.Selection(related='kpi_id.priority_weight', store=True)

    date = fields.Datetime(string="Submitted On", default=fields.Datetime.now)
    user_id = fields.Many2one('res.users', string="Submitted By", default=lambda self: self.env.user)
    value = fields.Float(string="Value")
    achievement_percent = fields.Float(
        string="Target Achievement (%)",
        compute="_compute_achievement",
        store=True,
        digits=(16, 2)
    )
    note = fields.Text(string="Note")

    score_label = fields.Char(string="Score Label")
    score_color = fields.Selection([
    ('0', 'Grey'),
    ('1', 'Green'),
    ('2', 'Blue'),
    ('3', 'Orange'),
    ('4', 'Yellow'),
    ('5', 'Darkred'),
], string="Score Color")

    @api.depends('value', 'target_value', 'target_type', 'kpi_direction')
    def _compute_achievement(self):
        for rec in self:
            if rec.target_type in ['number', 'percent', 'currency', 'duration']:
                if rec.kpi_direction == 'higher_better':
                    rec.achievement_percent = (rec.value / rec.target_value * 100) if rec.target_value else 0.0
                elif rec.kpi_direction == 'lower_better':
                    if rec.value == 0:
                        rec.achievement_percent = 100.0
                    else:
                        ratio = (rec.target_value / rec.value * 100) if rec.value else 0.0
                        rec.achievement_percent = min(ratio, 100.0)
            elif rec.target_type == 'boolean':
                rec.achievement_percent = 100.0 if rec.value else 0.0
            else:
                rec.achievement_percent = 0.0