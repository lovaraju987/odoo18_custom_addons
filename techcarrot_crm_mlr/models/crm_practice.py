# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CrmPractice(models.Model):
    _name = 'crm.practice'
    _description = 'CRM Practice'
    _order = 'name'

    name = fields.Char(string='Practice Name', required=True)
    code = fields.Char(string='Practice Code')
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Practice name must be unique!'),
    ]
    
    def name_get(self):
        """Return the display name for the practice."""
        result = []
        for practice in self:
            name = practice.name
            if practice.code:
                name = f"[{practice.code}] {name}"
            result.append((practice.id, name))
        return result
