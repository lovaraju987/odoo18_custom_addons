# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.onchange('partner_id')
    def _onchange_partner_id_point_of_contact_portal(self):
        """Auto-set point of contact when partner is selected in portal"""
        if self.partner_id:
            # If partner has child contacts, set the first one as point of contact
            contacts = self.partner_id.child_ids.filtered(lambda c: not c.is_company)
            if contacts and not self.point_of_contact_id:
                self.point_of_contact_id = contacts[0]
            elif not self.partner_id.is_company and not self.point_of_contact_id:
                # If no child contacts and partner itself is a person
                self.point_of_contact_id = self.partner_id

    @api.onchange('deal_manager_id')
    def _onchange_deal_manager_id_portal(self):
        """Set user_id based on deal manager in portal"""
        if self.deal_manager_id and self.deal_manager_id.user_id and not self.user_id:
            self.user_id = self.deal_manager_id.user_id
