from odoo import models, fields, api

class KPIReportSubmission(models.Model):
    _name = 'kpi.report.submission'
    _description = 'KPI Report Submission'
    _order = 'date desc'

    # SQL constraints for data integrity
    _sql_constraints = [
        ('unique_kpi_user_date', 'UNIQUE(kpi_id, user_id, date(date))', 'Only one submission per user per day'),
        ('achievement_percent_range', 'CHECK(achievement_percent >= 0)', 'Achievement percent cannot be negative'),
    ]

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
            rec.achievement_percent = rec._calculate_achievement_percent()

    def _calculate_achievement_percent(self):
        """Calculate achievement percentage based on target type and direction"""
        if self.target_type in ['number', 'percent', 'currency', 'duration']:
            return self._calculate_numeric_achievement()
        elif self.target_type == 'boolean':
            return 100.0 if self.value else 0.0
        else:
            return 0.0

    def _calculate_numeric_achievement(self):
        """Calculate achievement for numeric target types"""
        if self.kpi_direction == 'higher_better':
            return (self.value / self.target_value * 100) if self.target_value else 0.0
        elif self.kpi_direction == 'lower_better':
            if self.value == 0:
                return 100.0
            else:
                ratio = (self.target_value / self.value * 100) if self.value else 0.0
                return min(ratio, 100.0)
        return 0.0