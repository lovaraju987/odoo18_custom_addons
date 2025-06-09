# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


def validate_mandatory_field(field, kw):
    """Validates the mandatory fields of the Generate Lead form."""
    error = None
    data = {}
    for key, value in field.items():
        if not kw.get(key):
            error = "Necessary field " + value + " is missing"
            break
        data[key] = kw.get(key)
    return error, data


def validate_optional_fields(opt_fields, kw):
    """Validates the optional fields of the Generate Lead form."""
    data = {}
    for fld in opt_fields:
        if kw.get(fld):
            data[fld] = kw.get(fld)
    return data


def check_record_id(record_id):
    """
    Convert record_id(s) to int. Returns int for single ID, list of ints for multiple.
    Returns False if conversion fails.
    """
    try:
        if len(record_id) == 1:
            record_id = int(record_id)
            return record_id
        record_ids = []
        for number in record_id:
            record_ids.append(int(number))
        return record_ids
    except:
        return False


def get_static_data():
    """ Retrieve default values for CRM form fields."""

    partner = request.env.user.partner_id
    medium_ids = request.env['utm.medium'].sudo().search([])
    source_ids = request.env['utm.source'].sudo().search([])
    tag_ids = request.env['crm.tag'].sudo().search([])
    country_ids = request.env['res.country'].sudo().search([])
    form_data = {
        'partner': partner,
        'medium_ids': medium_ids,
        'source_ids': source_ids,
        'tag_ids': tag_ids,
        'country_ids': country_ids,
    }

    return form_data


class LeadPortal(CustomerPortal):
    """
     - Displaying the form view of the selected CRM lead (`crm.lead`)
      in read-only mode.
    - Showing a list of quotations (`sale.order`) that are specifically
      linked to this lead via the `opportunity_id` field.
    - Ensuring that the lead and its related data are only accessible
      to the currently logged-in portal user, improving data security
      and user-specific views.
    """

    @http.route(['/my/orders', '/my/orders/page/<int:page>'],
                type='http', auth='user', website=True)
    def portal_my_orders(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        """
        Redirects to the quotations related to the current CRM lead.
        """

        response = super().portal_my_orders(
            page=page, date_begin=date_begin, date_end=date_end, sortby=sortby, **kw)
        lead_id = kw.get('lead_id')
        if lead_id:
            orders = response.qcontext.get('orders', request.env['sale.order'])
            filtered_orders = orders.filtered(lambda o: o.opportunity_id.id == int(lead_id))
            response.qcontext['orders'] = filtered_orders
        return response

    @http.route('/generate/lead', type='http', auth='user', website=True)
    def generate_customer_leads(self):
        """
        This method creates new CRM lead records based on the provided data or
        predefined logic. It can be used to programmatically generate leads
        from external sources, user inputs.
        """

        return request.render('tk_portal_partner_leads.generate_lead_template', get_static_data())

    @http.route('/my/leads/submit', type='http', auth='user', website=True, csrf=True)
    def portal_form_submit_lead(self, **kw):
        """
        Handles submission of the lead form from the portal.
        """
        required_field = {
            'name': 'Title',
            'contact_name': 'Name'
        }
        optional_fields = ['email_from', 'phone', 'street', 'street2', 'city', 'zip',
                           'description']
        error, lead_data = validate_mandatory_field(required_field, kw)

        if error:
            form_data = get_static_data()
            form_data['error'] = error
            return request.render('tk_portal_partner_leads.generate_lead_template', form_data)

        lead_data['type'] = 'lead'
        if kw.get('source_id'):
            if not check_record_id(kw.get('source_id')):
                return request.redirect("/my/home")
            lead_data['source_id'] = kw.get('source_id')

        tag_ids = request.httprequest.form.getlist('tag_ids')
        if tag_ids:
            if not check_record_id(tag_ids):
                return request.redirect("/my/home")
            lead_data['tag_ids'] = [(6, 0, tag_ids)]

        if kw.get('medium_id'):
            if not check_record_id(kw.get('medium_id')):
                return request.redirect("/my/home")
            lead_data['medium_id'] = kw.get('medium_id')

        if kw.get('state_id'):
            state_id = kw.get('state_id').split('-')[0]
            if not check_record_id(state_id):
                return request.redirect("/my/home")
            lead_data['state_id'] = state_id

        if kw.get('country_id'):
            country_id = kw.get('country_id').split('-')[0]
            if not check_record_id(country_id):
                return request.redirect("/my/home")
            lead_data['country_id'] = country_id

        opt_data = validate_optional_fields(optional_fields, kw)
        lead_data.update(opt_data)
        lead_id = request.env['crm.lead'].sudo().create(lead_data)

        return request.redirect(f'/my/lead/{request.env["ir.http"]._slug(lead_id)}')


    @http.route('/get-state-data', type='json', auth="user", website=True)
    def get_state_data(self, **kw):
        """Get state data via country id"""
        country_id = kw.get('country_id').split('-')[0]
        if not isinstance(country_id, str) and country_id.isdigit():
            return {
                'status': False
            }
        country = request.env['res.country'].sudo().browse(int(country_id))
        if country.exists():
            state_ids = country.state_ids.ids
            state_names = country.state_ids.mapped('name')
            if len(state_names) <= 0:
                return {
                    'status': False
                }
            return {
                'status': True,
                'state_names': state_names,
                'state_ids': state_ids,
            }

    @http.route(['/my/leads', '/my/leads/page/<int:page>'], type='http', auth='user', website=True)
    def portal_my_leads(self, page=1, sortby='name', **kw):
        """
        Displays the CRM leads tree view filtered by the logged-in user.
        """
        partner_id = request.env.user.partner_id
        user_id = request.env.user
        lead_obj = request.env['crm.lead'].sudo()
        source_ids = request.env['utm.source'].sudo().search([])
        filter_source_id = kw.get('source')
        domain = ['|', ('partner_id', '=', partner_id.id), ('user_id', '=', user_id.id)]

        search = kw.get('search', '').strip()
        if search:
            domain += [('name', 'ilike', search)]
        if filter_source_id:
            domain += [('source_id', '=', int(filter_source_id))]

        items_per_page = 10
        total_leads = lead_obj.search_count(domain)

        sorted_list = {
            'name': {'label': 'Name', 'order': 'name asc'},
            'date': {'label': 'Assignation Date', 'order': 'create_date asc'},
        }
        order = sorted_list[sortby]['order']
        pager = portal_pager(
            url="/my/leads",
            total=total_leads,
            page=page,
            url_args={'sortby': sortby},
            step=items_per_page
        )

        leads = lead_obj.search(domain, order=order, limit=items_per_page, offset=pager['offset'])

        has_quotations = bool(request.env['sale.order'].sudo().search([
            ('partner_id', '=', partner_id.id),
            ('opportunity_id', 'in', leads.ids)
        ], limit=1))

        values = {
            'leads': leads,
            'has_quotations': has_quotations,
            'page_name': 'leads',
            'pager': pager,
            'sortby': sortby,
            'searchbar_sortings': sorted_list,
            'partner_id': partner_id,
            'user_id': user_id,
            'source_ids': source_ids,
        }

        return request.render('tk_portal_partner_leads.portal_my_leads', values)

    @http.route(["/my/lead/<model('crm.lead'):lead_id>"], type="http", auth="user", website=True)
    def action_view_lead_details(self, lead_id):
        """
        Displays the read-only form view of a CRM lead.
        """
        partner_id = request.env.user.partner_id
        user_id = request.env.user
        domain = ['|', ('partner_id', '=', partner_id.id), ('user_id', '=', user_id.id)]
        all_leads = request.env['crm.lead'].sudo().search(domain)
        lead_ids = all_leads.ids
        current_index = lead_ids.index(lead_id.id)
        prev_id = lead_ids[current_index - 1] if current_index > 0 else None
        next_id = lead_ids[current_index + 1] if current_index < len(lead_ids) - 1 else None
        values = {
            'lead': lead_id,
            'prev_record': f'/my/lead/{prev_id}' if prev_id else None,
            'next_record': f'/my/lead/{next_id}' if next_id else None,
            'page_name': 'leads_form_view',

        }

        return request.render('tk_portal_partner_leads.portal_my_leads_template_form_view', values)
