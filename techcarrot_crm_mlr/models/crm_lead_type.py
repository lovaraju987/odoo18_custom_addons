from odoo import models, fields

class CrmLeadType(models.Model):
    _name = 'crm.lead.type'
    _description = 'CRM Lead Type'
    _order = 'name'

    name = fields.Char(string='Type Name', required=True)
    code = fields.Char(string='Type Code')
    active = fields.Boolean(string='Active', default=True)

    def name_get(self):
        result = []
        for rec in self:
            display = f"{rec.code} - {rec.name}" if rec.code else rec.name
            result.append((rec.id, display))
        return result
