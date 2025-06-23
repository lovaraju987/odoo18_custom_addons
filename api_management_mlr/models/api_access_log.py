from odoo import models, fields, api

class ApiAccessLog(models.Model):
    _name = 'api.access.log'
    _description = 'API Access Log'
    _order = 'timestamp desc'

    api_key_id = fields.Many2one('res.api.key', string="API Key")
    endpoint = fields.Char(string="Endpoint")
    status = fields.Selection([
        ('success', 'Success'),
        ('unauthorized', 'Unauthorized'),
        ('fail', 'Fail')
    ], string="Status")
    timestamp = fields.Datetime(string="Timestamp", default=fields.Datetime.now)
    ip_address = fields.Char(string="IP Address")
    query_string = fields.Text(string="Query Params")