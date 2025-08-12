# controllers/main.py
from odoo import http, fields
from odoo.http import request
import html

# Constants for model names and URLs
CRM_TAG_MODEL = 'crm.tag'
CRM_REDIRECT_URL = '/my/employee/crm'
HR_EMPLOYEE_MODEL = 'hr.employee'
HR_ATTENDANCE_MODEL = 'hr.attendance'
CRM_LEAD_MODEL = 'crm.lead'
CRM_STAGE_MODEL = 'crm.stage'
MY_EMPLOYEE_URL = '/my/employee'

def _process_tag_ids(post):
    """Refactored to reduce cognitive complexity."""
    tag_ids = []
    # Get tag ids from post (handle both list and string cases)
    if hasattr(post, 'getlist'):
        tag_ids = post.getlist('tag_ids[]') or post.getlist('tag_ids')
    else:
        tag_ids = post.get('tag_ids[]', []) or post.get('tag_ids', [])
        if isinstance(tag_ids, str):
            tag_ids = tag_ids.split(',') if ',' in tag_ids else [tag_ids]
    if not isinstance(tag_ids, list):
        tag_ids = [tag_ids]
    tag_id_list = []
    for tag in tag_ids or []:
        if not tag:
            continue
        try:
            tag_id_list.append(int(tag))
        except (ValueError, TypeError):
            tag_rec = request.env[CRM_TAG_MODEL].sudo().search([('name', '=', tag)], limit=1)
            if not tag_rec:
                tag_rec = request.env[CRM_TAG_MODEL].sudo().create({'name': tag})
            tag_id_list.append(tag_rec.id)
    tag_id_list = [int(t) for t in tag_id_list if t]
    import logging
    _logger = logging.getLogger(__name__)
    _logger.info('ESS Portal: tag_id_list to write: %s', tag_id_list)
    return tag_id_list

class PortalEmployee(http.Controller):
    def _get_employee(self):
        return request.env[HR_EMPLOYEE_MODEL].sudo().search([('user_id', '=', request.uid)], limit=1)

    @http.route(MY_EMPLOYEE_URL, type='http', auth='user', website=True)
    def portal_employee_profile(self, **kw):
        employee = request.env[HR_EMPLOYEE_MODEL].sudo().search([('user_id', '=', request.uid)], limit=1)
        return request.render('employee_self_service_portal.portal_employee_profile_personal', {
            'employee': employee,
            'section': 'personal',
        })

    @http.route(MY_EMPLOYEE_URL + '/attendance/checkin', type='http', auth='user', methods=['POST'], website=True)
    def check_in(self, **post):
        employee = request.env[HR_EMPLOYEE_MODEL].sudo().search([('user_id', '=', request.uid)], limit=1)
        if not employee:
            return request.redirect(MY_EMPLOYEE_URL)
        try:
            in_latitude = post.get('in_latitude')
            in_longitude = post.get('in_longitude')
            check_in_location = post.get('check_in_location')
            vals = {
                'employee_id': employee.id,
                'check_in': fields.Datetime.now(),
            }
            if in_latitude:
                vals['in_latitude'] = in_latitude
            if in_longitude:
                vals['in_longitude'] = in_longitude
            if check_in_location:
                vals['check_in_location'] = check_in_location
            request.env[HR_ATTENDANCE_MODEL].sudo().create(vals)
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error("Check-in failed: %s", e)
            return request.redirect(MY_EMPLOYEE_URL)
        return request.redirect(MY_EMPLOYEE_URL + '/attendance')

    @http.route(MY_EMPLOYEE_URL + '/attendance/checkout', type='http', auth='user', methods=['POST'], website=True)
    def check_out(self, **post):
        employee = request.env[HR_EMPLOYEE_MODEL].sudo().search([('user_id', '=', request.uid)], limit=1)
        if not employee:
            return request.redirect(MY_EMPLOYEE_URL)
        last_attendance = request.env[HR_ATTENDANCE_MODEL].sudo().search(
            [('employee_id', '=', employee.id)], order='check_in desc', limit=1)
        if last_attendance and not last_attendance.check_out:
            out_latitude = post.get('out_latitude')
            out_longitude = post.get('out_longitude')
            check_out_location = post.get('check_out_location')
            vals = {
                'check_out': fields.Datetime.now(),
            }
            if out_latitude:
                vals['out_latitude'] = out_latitude
            if out_longitude:
                vals['out_longitude'] = out_longitude
            if check_out_location:
                vals['check_out_location'] = check_out_location
            last_attendance.sudo().write(vals)
            # Debug log to check values after checkout
            import logging
            _logger = logging.getLogger(__name__)
            # Re-browse the record to get updated computed fields
            updated_attendance = request.env[HR_ATTENDANCE_MODEL].sudo().browse(last_attendance.id)
            _logger.info(f"Attendance Debug: check_in={updated_attendance.check_in}, check_out={updated_attendance.check_out}, worked_hours={updated_attendance.worked_hours}")
        return request.redirect(MY_EMPLOYEE_URL + '/attendance')
    
    @http.route(MY_EMPLOYEE_URL + '/attendance', type='http', auth='user', website=True)
    def portal_attendance_history(self, **kwargs):
        from datetime import datetime
        employee = request.env[HR_EMPLOYEE_MODEL].sudo().search([('user_id', '=', request.uid)], limit=1)
        now = datetime.now()
        # Use current month/year as default if not provided
        month = int(kwargs.get('month', now.month))
        year = int(kwargs.get('year', now.year))
        domain = [('employee_id', '=', employee.id)]
        if month and year:
            from calendar import monthrange
            start_date = datetime(year, month, 1)
            end_date = datetime(year, month, monthrange(year, month)[1], 23, 59, 59)
            domain += [('check_in', '>=', start_date.strftime('%Y-%m-%d 00:00:00')),
                       ('check_in', '<=', end_date.strftime('%Y-%m-%d 23:59:59'))]
        attendances = request.env[HR_ATTENDANCE_MODEL].sudo().search(
            domain, order='check_in desc', limit=20)
        today_att = None
        today_str = now.strftime('%Y-%m-%d')
        if attendances and attendances[0].check_in:
            if attendances[0].check_in.strftime('%Y-%m-%d') == today_str:
                today_att = attendances[0]
        # For dropdowns
        current_year = now.year
        years = list(range(current_year - 5, current_year + 2))
        months = [
            {'value': i, 'name': datetime(2000, i, 1).strftime('%B')} for i in range(1, 13)
        ]
        return request.render('employee_self_service_portal.portal_attendance', {
            'attendances': attendances,
            'employee': employee,
            'today_att': today_att,
            'selected_month': month,
            'selected_year': year,
            'years': years,
            'months': months,
        })

    @http.route(MY_EMPLOYEE_URL + '/edit', type='http', auth='user', website=True, methods=['GET', 'POST'])
    def portal_employee_edit(self, **post):
        employee = request.env[HR_EMPLOYEE_MODEL].sudo().search([('user_id', '=', request.uid)], limit=1)
        if not employee:
            return request.redirect(MY_EMPLOYEE_URL)
        if http.request.httprequest.method == 'POST':
            vals = {}
            # Personal Details
            vals['work_email'] = post.get('work_email')
            vals['work_phone'] = post.get('work_phone')
            vals['birthday'] = post.get('birthday')
            vals['gender'] = post.get('gender')
            vals['marital'] = post.get('marital')
            # Experience & Skills
            vals['x_experience'] = post.get('x_experience')
            vals['x_skills'] = post.get('x_skills')
            # Certifications
            vals['x_certifications'] = post.get('x_certifications')
            # Bank Details
            vals['x_bank_account'] = post.get('x_bank_account')
            vals['x_bank_name'] = post.get('x_bank_name')
            vals['x_ifsc'] = post.get('x_ifsc')
            # Only update fields that are present in the form
            vals = {k: v for k, v in vals.items() if v is not None}
            if vals:
                employee.sudo().write(vals)
            return request.redirect(MY_EMPLOYEE_URL)
        return request.render('employee_self_service_portal.portal_employee_edit', {
            'employee': employee,
        })

    @http.route('/my/ess', type='http', auth='user', website=True)
    def portal_ess_dashboard(self, **kwargs):
        return request.render('employee_self_service_portal.portal_ess_dashboard')

    @http.route(MY_EMPLOYEE_URL + '/personal', type='http', auth='user', website=True, methods=['GET', 'POST'])
    def portal_employee_personal(self, **post):
        employee = self._get_employee()
        if request.httprequest.method == 'POST':
            # update personal details
            vals = {
                'work_email': post.get('work_email'),
                'work_phone': post.get('work_phone'),
                'birthday': post.get('birthday'),
                'gender': post.get('gender'),
                'marital': post.get('marital'),
            }
            employee.sudo().write({k: v for k, v in vals.items() if v is not None})
        return request.render('employee_self_service_portal.portal_employee_profile_personal', {
            'employee': employee,
            'section': 'personal',
        })

    @http.route(MY_EMPLOYEE_URL + '/experience', type='http', auth='user', website=True, methods=['GET', 'POST'])
    def portal_employee_experience(self, **post):
        employee = self._get_employee()
        if request.httprequest.method == 'POST':
            vals = {
                'x_experience': post.get('x_experience'),
                'x_skills': post.get('x_skills'),
            }
            employee.sudo().write({k: v for k, v in vals.items() if v is not None})
        return request.render('employee_self_service_portal.portal_employee_profile_experience', {
            'employee': employee,
            'section': 'experience',
        })

    @http.route(MY_EMPLOYEE_URL + '/certification', type='http', auth='user', website=True, methods=['GET', 'POST'])
    def portal_employee_certification(self, **post):
        employee = self._get_employee()
        if request.httprequest.method == 'POST':
            vals = {
                'x_certifications': post.get('x_certifications'),
            }
            employee.sudo().write({k: v for k, v in vals.items() if v is not None})
        return request.render('employee_self_service_portal.portal_employee_profile_certification', {
            'employee': employee,
            'section': 'certification',
        })

    @http.route(MY_EMPLOYEE_URL + '/bank', type='http', auth='user', website=True, methods=['GET', 'POST'])
    def portal_employee_bank(self, **post):
        employee = self._get_employee()
        if request.httprequest.method == 'POST':
            vals = {
                'x_bank_account': post.get('x_bank_account'),
                'x_bank_name': post.get('x_bank_name'),
                'x_ifsc': post.get('x_ifsc'),
            }
            employee.sudo().write({k: v for k, v in vals.items() if v is not None})
        return request.render('employee_self_service_portal.portal_employee_profile_bank', {
            'employee': employee,
            'section': 'bank',
        })

    @http.route('/my/employee/crm', type='http', auth='user', website=True)
    def portal_employee_crm(self, **kwargs):
        employee = self._get_employee()
        user = request.env.user
        leads = request.env['crm.lead'].sudo().search([
            ('user_id', '=', user.id)
        ], order='priority desc, date_deadline asc')
        return request.render('employee_self_service_portal.portal_employee_crm', {
            'employee': employee,
            'leads': leads,
        })

    @http.route('/my/employee/crm/create', type='http', auth='user', website=True, methods=['GET', 'POST'])
    def portal_employee_crm_create(self, **post):
        user = request.env.user
        if request.httprequest.method == 'POST':
            vals = {
                'name': post.get('name'),
                'partner_id': post.get('partner_id') or False,
                'email_from': post.get('email_from'),
                'phone': post.get('phone'),
                'expected_revenue': post.get('expected_revenue') or 0.0,
                'user_id': user.id,
                'stage_id': post.get('stage_id') or False,
                'description': post.get('description'),
                'probability': post.get('probability') or 0.0,
                'date_deadline': post.get('date_deadline') or False,
            }
            lead = request.env['crm.lead'].sudo().create(vals)
            tag_id_list = _process_tag_ids(post)
            # Always update tag_ids, even if empty (to allow clearing all tags)
            lead.sudo().write({'tag_ids': [(6, 0, tag_id_list)]})
            return request.redirect(CRM_REDIRECT_URL)
        partners = request.env['res.partner'].sudo().search([], limit=50)
        stages = request.env['crm.stage'].sudo().search([])
        all_tags = request.env[CRM_TAG_MODEL].sudo().search([])
        # Show all users (internal and portal) as salespersons
        salespersons = request.env['res.users'].sudo().search([('active', '=', True)], limit=100)
        current_user_id = request.env.user.id
        return request.render('employee_self_service_portal.portal_employee_crm_create', {
            'partners': partners,
            'stages': stages,
            'all_tags': all_tags,
            'salespersons': salespersons,
            'current_user_id': current_user_id,
        })

    @http.route('/my/employee/crm/edit/<int:lead_id>', type='http', auth='user', website=True, methods=['GET', 'POST'])
    def portal_employee_crm_edit(self, lead_id, **post):
        lead = request.env[CRM_LEAD_MODEL].sudo().browse(lead_id)
        user = request.env.user
        if not lead or lead.user_id.id != user.id:
            return request.redirect(CRM_REDIRECT_URL)
        if request.httprequest.method == 'POST':
            vals = {
                'name': post.get('name'),
                'email_from': post.get('email_from'),
                'phone': post.get('phone'),
                'description': post.get('description'),
                'date_deadline': post.get('date_deadline'),
            }
            # Convert probability and expected_revenue to float if present
            prob = post.get('probability')
            if prob:
                try:
                    vals['probability'] = float(prob)
                except Exception:
                    pass
            exp_rev = post.get('expected_revenue')
            if exp_rev:
                try:
                    vals['expected_revenue'] = float(exp_rev)
                except Exception:
                    pass
            # Validate stage_id
            stage_id = post.get('stage_id')
            if stage_id:
                try:
                    stage_id_int = int(stage_id)
                    stage = request.env[CRM_STAGE_MODEL].sudo().browse(stage_id_int)
                    if stage.exists():
                        vals['stage_id'] = stage_id_int
                except Exception:
                    pass
            lead.sudo().write({k: v for k, v in vals.items() if v is not None})
            tag_id_list = _process_tag_ids(post)
            lead.sudo().write({'tag_ids': [(6, 0, tag_id_list)]})
            return request.redirect(CRM_REDIRECT_URL)
        stages = request.env[CRM_STAGE_MODEL].sudo().search([])
        partners = request.env['res.partner'].sudo().search([], limit=50)
        all_tags = request.env[CRM_TAG_MODEL].sudo().search([])
        salespersons = request.env['res.users'].sudo().search([('active', '=', True)], limit=100)
        activity_types = request.env['mail.activity.type'].sudo().search([])
        default_activity_type_id = request.env.ref('mail.mail_activity_data_todo').id if request.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False) else (activity_types and activity_types[0].id or False)
        return request.render('employee_self_service_portal.portal_employee_crm_edit', {
            'lead': lead,
            'stages': stages,
            'all_tags': all_tags,
            'partners': partners,
            'salespersons': salespersons,
            'activity_types': activity_types,
            'default_activity_type_id': default_activity_type_id,
        })

    @http.route('/my/employee/crm/delete/<int:lead_id>', type='http', auth='user', website=True, methods=['POST'])
    def portal_employee_crm_delete(self, lead_id, **post):
        lead = request.env['crm.lead'].sudo().browse(lead_id)
        user = request.env.user
        if lead and lead.user_id.id == user.id:
            lead.sudo().unlink()
        return request.redirect('/my/employee/crm')

    @http.route('/my/employee/crm/log_note/<int:lead_id>', type='http', auth='user', website=True, methods=['POST'])
    def portal_employee_crm_log_note(self, lead_id, **post):
        import logging
        _logger = logging.getLogger(__name__)
        lead = request.env[CRM_LEAD_MODEL].sudo().browse(lead_id)
        user = request.env.user
        note = post.get('note')
        file_keys = list(request.httprequest.files.keys())
        _logger.info('ESS Portal: Received file keys: %s', file_keys)
        files = []
        if hasattr(request.httprequest.files, 'getlist'):
            files = request.httprequest.files.getlist('attachments')
        elif 'attachments' in request.httprequest.files:
            file = request.httprequest.files['attachments']
            if file:
                files = [file]
        _logger.info('ESS Portal: Number of files in attachments: %s', len(files))
        for f in files:
            _logger.info('ESS Portal: File received: filename=%s content_type=%s', getattr(f, 'filename', None), getattr(f, 'content_type', None))
        # Allow log note with or without text, as long as there are files or a note
        if lead and (note or files) and lead.user_id.id == user.id:
            msg = lead.message_post(body=note or '', message_type='comment', author_id=user.partner_id.id)
            import base64
            attachment_ids = []
            for file in files:
                try:
                    file.seek(0)
                except Exception:
                    pass
                file_content = file.read()
                if file_content:
                    if isinstance(file_content, str):
                        file_content = file_content.encode('utf-8')
                    encoded_content = base64.b64encode(file_content).decode('utf-8')
                    attachment = request.env['ir.attachment'].sudo().create({
                        'name': file.filename,
                        'datas': encoded_content,
                        'res_model': 'crm.lead',
                        'res_id': lead.id,
                        'mimetype': file.mimetype,
                        'type': 'binary',
                        'public': True,
                    })
                    attachment_ids.append(attachment.id)
                    _logger.info('ESS Portal: Created attachment id=%s name=%s res_model=%s res_id=%s', attachment.id, attachment.name, attachment.res_model, attachment.res_id)
            if attachment_ids:
                msg.sudo().write({'attachment_ids': [(4, att_id) for att_id in attachment_ids]})
        return request.redirect(f'/my/employee/crm/edit/{lead_id}')

    @http.route('/my/employee/crm/add_activity/<int:lead_id>', type='http', auth='user', website=True, methods=['POST'])
    def portal_employee_crm_add_activity(self, lead_id, **post):
        lead = request.env['crm.lead'].sudo().browse(lead_id)
        user = request.env.user
        summary = post.get('summary')
        date_deadline = post.get('date_deadline')
        note = post.get('note')
        activity_type_id = post.get('activity_type_id')
        assigned_user_id = post.get('assigned_user_id')
        if lead and summary and date_deadline and lead.user_id.id == user.id:
            activity_type_xmlid = None
            activity_type_name = ''
            if activity_type_id:
                activity_type = request.env['mail.activity.type'].sudo().browse(int(activity_type_id))
                external_ids = activity_type.get_external_id()
                activity_type_xmlid = external_ids.get(activity_type.id)
                activity_type_name = activity_type.name
            if not activity_type_xmlid:
                activity_type_xmlid = 'mail.mail_activity_data_todo'
                activity_type_name = 'To Do'
            assigned_uid = int(assigned_user_id) if assigned_user_id else user.id
            assigned_user = request.env['res.users'].sudo().browse(assigned_uid)
            lead.activity_schedule(
                activity_type_xmlid,
                summary=summary,
                note=note,
                date_deadline=date_deadline,
                user_id=assigned_uid
            )
            # Log in chatter, escape note
            msg = f"Activity created: <b>{activity_type_name}</b> - <b>{summary}</b> (Assigned to: {assigned_user.name}, Due: {date_deadline})"
            if note:
                msg += f"<br/>Note: {html.escape(note)}"
            lead.message_post(body=msg)
        return request.redirect(f'/my/employee/crm/edit/{lead_id}')

    @http.route('/my/employee/crm/activity_done/<int:activity_id>', type='http', auth='user', website=True, methods=['POST'])
    def portal_employee_crm_activity_done(self, activity_id, **post):
        activity = request.env['mail.activity'].sudo().browse(activity_id)
        lead_id = int(request.params.get('lead_id', 0))
        lead = request.env['crm.lead'].sudo().browse(lead_id)
        user = request.env.user
        # Security: Only allow if user owns the lead
        if activity and lead and lead.user_id.id == user.id and activity.res_model == 'crm.lead' and activity.res_id == lead.id:
            try:
                activity.action_done()
            except Exception:
                pass
        return request.redirect(f'/my/employee/crm/edit/{lead_id}')

    @http.route('/my/employee/crm/activity_edit/<int:activity_id>', type='http', auth='user', website=True, methods=['GET', 'POST'])
    def portal_employee_crm_activity_edit(self, activity_id, **post):
        activity = request.env['mail.activity'].sudo().browse(activity_id)
        lead_id = int(request.params.get('lead_id', 0))
        lead = request.env['crm.lead'].sudo().browse(lead_id)
        user = request.env.user
        if not (activity and lead and lead.user_id.id == user.id and activity.res_model == 'crm.lead' and activity.res_id == lead.id):
            return request.redirect(f'/my/employee/crm/edit/{lead_id}')
        if request.httprequest.method == 'POST':
            vals = {}
            if post.get('summary') is not None:
                vals['summary'] = post.get('summary')
            if post.get('date_deadline') is not None:
                vals['date_deadline'] = post.get('date_deadline')
            if post.get('note') is not None:
                vals['note'] = post.get('note')
            if post.get('activity_type_id'):
                vals['activity_type_id'] = int(post.get('activity_type_id'))
            if post.get('user_id'):
                vals['user_id'] = int(post.get('user_id'))
            if vals:
                activity.sudo().write(vals)
                # Log in chatter, escape note
                activity_type_name = activity.activity_type_id.name or ''
                assigned_user = activity.user_id
                msg = f"Activity updated: <b>{activity_type_name}</b> - <b>{activity.summary}</b> (Assigned to: {assigned_user.name}, Due: {activity.date_deadline})"
                if activity.note:
                    msg += f"<br/>Note: {html.escape(activity.note)}"
                lead.message_post(body=msg)
            return request.redirect(f'/my/employee/crm/edit/{lead_id}')
        # GET: render a simple edit form (reuse activity_types and salespersons from lead edit)
        activity_types = request.env['mail.activity.type'].sudo().search([])
        salespersons = request.env['res.users'].sudo().search([('active', '=', True)], limit=100)
        return request.render('employee_self_service_portal.portal_employee_crm_activity_edit', {
            'activity': activity,
            'lead': lead,
            'activity_types': activity_types,
            'salespersons': salespersons,
        })

    @http.route('/my/employee/crm/activity_delete/<int:activity_id>', type='http', auth='user', website=True, methods=['POST'])
    def portal_employee_crm_activity_delete(self, activity_id, **post):
        activity = request.env['mail.activity'].sudo().browse(activity_id)
        lead_id = int(request.params.get('lead_id', 0))
        lead = request.env['crm.lead'].sudo().browse(lead_id)
        user = request.env.user
        if activity and lead and lead.user_id.id == user.id and activity.res_model == 'crm.lead' and activity.res_id == lead.id:
            try:
                activity_type_name = activity.activity_type_id.name or ''
                summary = activity.summary or ''
                assigned_user = activity.user_id
                due = activity.date_deadline or ''
                note = activity.note or ''
                msg = f"Activity deleted: <b>{activity_type_name}</b> - <b>{summary}</b> (Assigned to: {assigned_user.name}, Due: {due})"
                if note:
                    msg += f"<br/>Note: {html.escape(note)}"
                activity.sudo().unlink()
                lead.message_post(body=msg)
            except Exception:
                pass
        return request.redirect(f'/my/employee/crm/edit/{lead_id}')

    @http.route(MY_EMPLOYEE_URL + '/expenses', type='http', auth='user', website=True)
    def portal_expense_history(self, **kwargs):
        employee = request.env[HR_EMPLOYEE_MODEL].sudo().search([('user_id', '=', request.uid)], limit=1)
        domain = [('employee_id', '=', employee.id)]
        # Filtering logic
        status = kwargs.get('status')
        if status:
            if status == 'withdrawn' or status == 'cancel':
                domain += [('sheet_id.state', '=', 'cancel')]
            else:
                domain += [('sheet_id.state', '=', status)]
        category = kwargs.get('category')
        if category:
            domain += [('product_id', '=', int(category))]
        date = kwargs.get('date')
        if date:
            domain += [('date', '=', date)]
        expenses = request.env['hr.expense'].sudo().search(domain, order='date desc', limit=50)
        categories = request.env['product.product'].sudo().search([('can_be_expensed', '=', True)])
        return request.render('employee_self_service_portal.portal_expense', {
            'expenses': expenses,
            'employee': employee,
            'categories': categories,
            'selected_status': status or '',
            'selected_category': category or '',  # Pass as string
            'selected_date': date or '',
        })

    @http.route(MY_EMPLOYEE_URL + '/expenses/submit', type='http', auth='user', website=True, methods=['GET', 'POST'])
    def portal_expense_submit(self, **post):
        employee = request.env[HR_EMPLOYEE_MODEL].sudo().search([('user_id', '=', request.uid)], limit=1)
        # Use product_id as category (many2one to product.product, can_be_expensed=True)
        categories = request.env['product.product'].sudo().search([('can_be_expensed', '=', True)])
        error = None
        success = None
        if request.httprequest.method == 'POST':
            name = post.get('name')
            date = post.get('date')
            total_amount = post.get('total_amount')
            category_id = post.get('category_id')
            notes = post.get('notes')  # Get notes from form
            attachment = request.httprequest.files.get('attachment')
            if not (name and date and total_amount and category_id):
                error = 'All fields except attachment are required.'
            else:
                try:
                    vals = {
                        'name': name,
                        'date': date,
                        'employee_id': employee.id,
                        'total_amount': float(total_amount),
                        'product_id': int(category_id),
                        'description': notes,  # Save notes to description field
                    }
                    expense = request.env['hr.expense'].sudo().create(vals)
                    # Find or create an open expense report for this employee
                    sheet = request.env['hr.expense.sheet'].sudo().search([
                        ('employee_id', '=', employee.id),
                        ('state', '=', 'draft')
                    ], limit=1)
                    if not sheet:
                        sheet = request.env['hr.expense.sheet'].sudo().create({
                            'name': 'Expense Report',  # Required field
                            'employee_id': employee.id,
                            'expense_line_ids': [(4, expense.id)],
                        })
                    else:
                        sheet.write({'expense_line_ids': [(4, expense.id)]})
                    # Submit the report (send to manager)
                    if sheet.state == 'draft':
                        sheet.action_submit_sheet()
                    success = 'Expense submitted successfully.'
                except Exception as e:
                    error = 'Error submitting expense: %s' % str(e)
        return request.render('employee_self_service_portal.portal_expense_submit', {
            'employee': employee,
            'categories': categories,
            'error': error,
            'success': success,
        })

    @http.route(MY_EMPLOYEE_URL + '/expenses/withdraw/<int:expense_id>', type='http', auth='user', website=True, methods=['POST'])
    def portal_expense_withdraw(self, expense_id, **post):
        expense = request.env['hr.expense'].sudo().browse(expense_id)
        employee = request.env[HR_EMPLOYEE_MODEL].sudo().search([('user_id', '=', request.uid)], limit=1)
        # Only allow withdraw if expense is in submitted state and belongs to the current employee
        if expense and expense.employee_id.id == employee.id and expense.sheet_id and expense.sheet_id.state == 'submit':
            # Set the report to cancelled (withdraw)
            expense.sheet_id.write({'state': 'cancel'})
        return request.redirect(MY_EMPLOYEE_URL + '/expenses')

    @http.route(MY_EMPLOYEE_URL + '/payslips', type='http', auth='user', website=True)
    def portal_payslips_history(self, **kwargs):
        employee = request.env[HR_EMPLOYEE_MODEL].sudo().search([('user_id', '=', request.uid)], limit=1)
        domain = [('employee_id', '=', employee.id)]
        
        # Filtering logic
        status = kwargs.get('status')
        if status:
            domain += [('state', '=', status)]
        
        year = kwargs.get('year')
        if year:
            domain += [('date_from', '>=', f'{year}-01-01'), ('date_from', '<=', f'{year}-12-31')]
        
        month = kwargs.get('month')
        if month and year:
            domain += [('date_from', '>=', f'{year}-{month:02d}-01')]
            if month == 12:
                domain += [('date_from', '<=', f'{year}-{month:02d}-31')]
            else:
                # Get last day of month
                import calendar
                last_day = calendar.monthrange(int(year), int(month))[1]
                domain += [('date_from', '<=', f'{year}-{month:02d}-{last_day}')]
        
        payslips = request.env['hr.payslip'].sudo().search(domain, order='date_from desc', limit=50)
        
        # For filter dropdowns
        from datetime import datetime
        current_year = datetime.now().year
        years = list(range(current_year - 5, current_year + 1))
        months = [
            {'value': i, 'name': datetime(2000, i, 1).strftime('%B')} for i in range(1, 13)
        ]
        
        return request.render('employee_self_service_portal.portal_payslips', {
            'payslips': payslips,
            'employee': employee,
            'selected_status': status or '',
            'selected_year': year or '',
            'selected_month': month or '',
            'years': years,
            'months': months,
        })

    @http.route(MY_EMPLOYEE_URL + '/payslips/download/<int:payslip_id>', type='http', auth='user', website=True)
    def portal_payslip_download(self, payslip_id, **kwargs):
        employee = request.env[HR_EMPLOYEE_MODEL].sudo().search([('user_id', '=', request.uid)], limit=1)
        payslip = request.env['hr.payslip'].sudo().search([
            ('id', '=', payslip_id),
            ('employee_id', '=', employee.id)
        ], limit=1)
        
        if not payslip:
            return request.redirect(MY_EMPLOYEE_URL + '/payslips')
        
        # Generate PDF report
        report = request.env.ref('om_hr_payroll.payslip_details_report')
        pdf, _ = report.sudo()._render_qweb_pdf([payslip.id])
        
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf)),
            ('Content-Disposition', f'attachment; filename="Payslip-{payslip.employee_id.name}-{payslip.date_from}.pdf"')
        ]
        
        return request.make_response(pdf, headers=pdfhttpheaders)

    @http.route(MY_EMPLOYEE_URL + '/payslips/view/<int:payslip_id>', type='http', auth='user', website=True)
    def portal_payslip_view(self, payslip_id, **kwargs):
        employee = request.env[HR_EMPLOYEE_MODEL].sudo().search([('user_id', '=', request.uid)], limit=1)
        payslip = request.env['hr.payslip'].sudo().search([
            ('id', '=', payslip_id),
            ('employee_id', '=', employee.id)
        ], limit=1)
        
        if not payslip:
            return request.redirect(MY_EMPLOYEE_URL + '/payslips')
        
        return request.render('employee_self_service_portal.portal_payslip_view', {
            'payslip': payslip,
            'employee': employee,
        })
