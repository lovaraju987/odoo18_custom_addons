# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # Point of contact - links to contacts records
    point_of_contact_id = fields.Many2one(
        'res.partner',
        string='Point of Contact',
        domain="[('is_company', '=', False)]",
        help="Main contact person for this opportunity"
    )

    # Practice - many2one field
    practice_id = fields.Many2one(
        'crm.practice',
        string='Practice',
        help="Practice area for this opportunity"
    )

    # Deal manager - links to employee records
    deal_manager_id = fields.Many2one(
        'hr.employee',
        string='Deal Manager',
        help="Employee responsible for managing this deal"
    )

    # Proposal submission date - date field
    proposal_submission_date = fields.Date(
        string='Proposal Submission Date',
        help="Date when the proposal was submitted to the customer"
    )

    # Engaged Presales - checkbox
    engaged_presales = fields.Boolean(
        string='Engaged Presales',
        default=False,
        help="Check if presales team is engaged for this opportunity"
    )

    # Industry - many2one field
    industry_id = fields.Many2one(
        'crm.industry',
        string='Industry',
        help="Industry sector of the customer"
    )

    @api.onchange('partner_id')
    def _onchange_partner_id_point_of_contact(self):
        """Auto-set point of contact when partner is selected"""
        if self.partner_id:
            # If partner has child contacts, set the first one as point of contact
            contacts = self.partner_id.child_ids.filtered(lambda c: not c.is_company)
            if contacts:
                self.point_of_contact_id = contacts[0]
            else:
                # If no child contacts, check if partner itself is a person
                if not self.partner_id.is_company:
                    self.point_of_contact_id = self.partner_id
                else:
                    self.point_of_contact_id = False

    @api.onchange('deal_manager_id')
    def _onchange_deal_manager_id(self):
        """Set user_id based on deal manager"""
        if self.deal_manager_id and self.deal_manager_id.user_id:
            self.user_id = self.deal_manager_id.user_id
