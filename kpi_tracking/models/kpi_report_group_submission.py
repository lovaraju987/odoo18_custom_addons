from odoo import models, fields, api


class KPIReportGroupSubmission(models.Model):
    _name = 'kpi.report.group.submission'
    _description = 'KPI Report Group Submission History'
    _order = 'date desc'

    report_id = fields.Many2one('kpi.report.group', required=True, ondelete='cascade')
    date = fields.Datetime(string="Submitted At", default=fields.Datetime.now)    
    value = fields.Float(string="Achievement (%)")
    user_id = fields.Many2one('res.users', string="Updated By", default=lambda self: self.env.user)
    note = fields.Text()

    score_label = fields.Char(string="Score Label")
    score_color = fields.Selection([
    ('0', 'Grey'),
    ('1', 'Green'),
    ('2', 'Blue'),
    ('3', 'Orange'),
    ('4', 'Yellow'),
    ('5', 'Darkred'),
], string="Group Score Color")