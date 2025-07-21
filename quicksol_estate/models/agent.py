from odoo import models, fields

class Agent(models.Model):
    _name = 'real.estate.agent'
    _description = 'Agent'

    name = fields.Char(string='Agent Name', required=True)
    phone = fields.Char(string='Phone Number')
    email = fields.Char(string='Email')
    properties = fields.One2many('real.estate.property', 'agent_id', string='Properties')
    agency_name = fields.Char('Agency Name')
    years_experience = fields.Integer('Years of Experience')
    profile_picture = fields.Binary('Profile Picture')