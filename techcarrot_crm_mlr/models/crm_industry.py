# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CrmIndustry(models.Model):
    _name = 'crm.industry'
    _description = 'CRM Industry'
    _order = 'name'

    name = fields.Char(string='Industry Name', required=True)
    code = fields.Char(string='Industry Code')
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Industry name must be unique!'),
    ]
    
    def name_get(self):
        """Return the display name for the industry."""
        result = []
        for industry in self:
            name = industry.name
            if industry.code:
                name = f"[{industry.code}] {name}"
            result.append((industry.id, name))
        return result
