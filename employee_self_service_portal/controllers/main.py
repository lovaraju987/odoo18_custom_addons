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
        # By default, show only confirmed payslips
        domain = [('employee_id', '=', employee.id), ('state', '=', 'done')]
        
        # For filter dropdowns and defaults
        from datetime import datetime
        current_year = datetime.now().year
        
        # Filtering logic - convert to int and set defaults
        year = kwargs.get('year')
        if year:
            try:
                year = int(year)
            except (ValueError, TypeError):
                year = current_year
        else:
            year = current_year  # Default to current year
            
        month = kwargs.get('month')
        if month:
            try:
                month = int(month)
            except (ValueError, TypeError):
                month = None
        else:
            month = None  # Default to all months (no month filter)
        
        # Apply year filter (always applied)
        domain += [('date_from', '>=', f'{year}-01-01'), ('date_from', '<=', f'{year}-12-31')]
        
        # Apply month filter only if specified
        if month:
            domain += [('date_from', '>=', f'{year}-{month:02d}-01')]
            if month == 12:
                domain += [('date_from', '<=', f'{year}-{month:02d}-31')]
            else:
                # Get last day of month
                import calendar
                last_day = calendar.monthrange(year, month)[1]
                domain += [('date_from', '<=', f'{year}-{month:02d}-{last_day}')]
        
        payslips = request.env['hr.payslip'].sudo().search(domain, order='date_from desc', limit=50)
        
        # For filter dropdowns - make sure years are in descending order
        years = list(range(current_year, current_year - 6, -1))  # Current year first
        months = [
            {'value': i, 'name': datetime(2000, i, 1).strftime('%B')} for i in range(1, 13)
        ]
        
        return request.render('employee_self_service_portal.portal_payslips', {
            'payslips': payslips,
            'employee': employee,
            'selected_year': year,  # Always show the year being filtered
            'selected_month': month if month else '',  # Show selected month or empty string for "All Months"
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
        
        try:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.info("Attempting to generate PDF for payslip %s", payslip_id)
            
            # Use a simpler approach - try to generate PDF directly using sudo privileges
            # Try different report XML IDs that might be available
            report_xml_ids = [
                'om_hr_payroll.payslip_details_report',
                'om_hr_payroll.action_report_payslip',
                'hr_payroll.action_report_payslip',
                'hr_payroll.payslip_details_report'
            ]
            
            pdf_content = None
            report_name = None
            
            for xml_id in report_xml_ids:
                try:
                    _logger.info("Trying to generate PDF with report: %s", xml_id)
                    # Use sudo() to bypass permission issues and render directly
                    report = request.env.ref(xml_id, raise_if_not_found=False)
                    if report:
                        pdf_content = report.sudo()._render_qweb_pdf(payslip.ids)[0]
                        if pdf_content:
                            report_name = xml_id
                            _logger.info("Successfully generated PDF using report: %s", xml_id)
                            break
                except Exception as e:
                    _logger.debug("Failed with report %s: %s", xml_id, str(e))
                    continue
            
            # Fallback: If no specific report works, try to find any payslip report and use it
            if not pdf_content:
                _logger.info("Trying fallback method - searching for any payslip report")
                try:
                    # Search for any report on hr.payslip model using sudo
                    reports = request.env['ir.actions.report'].sudo().search([
                        ('model', '=', 'hr.payslip'),
                        ('report_type', '=', 'qweb-pdf')
                    ], limit=1)
                    
                    if reports:
                        report_name = reports[0].report_name or 'payslip_report'
                        _logger.info("Found fallback report: %s", report_name)
                        pdf_content = reports[0].sudo()._render_qweb_pdf(payslip.ids)[0]
                        _logger.info("Successfully generated PDF using fallback report")
                except Exception as e:
                    _logger.error("Fallback method also failed: %s", str(e))
            
            # Final fallback: try to use the report model directly
            if not pdf_content:
                _logger.info("Trying final fallback - direct report generation")
                try:
                    # Try generating with a generic report name
                    pdf_content = request.env['ir.actions.report'].sudo()._render_qweb_pdf(
                        'om_hr_payroll.payslip_details_report', payslip.ids)[0]
                    report_name = 'om_hr_payroll.payslip_details_report'
                    _logger.info("Final fallback succeeded")
                except Exception as e:
                    _logger.error("Final fallback failed: %s", str(e))
            
            if not pdf_content:
                _logger.error("All PDF generation methods failed")
                return request.redirect(MY_EMPLOYEE_URL + '/payslips?error=no_report_available')
            
            # Clean filename
            safe_name = payslip.employee_id.name.replace(' ', '_').replace('/', '_').replace('\\', '_')
            filename = f"Payslip-{safe_name}-{payslip.date_from}.pdf"
            
            _logger.info("Successfully generated PDF file: %s using report: %s", filename, report_name)
            
            pdfhttpheaders = [
                ('Content-Type', 'application/pdf'),
                ('Content-Length', len(pdf_content)),
                ('Content-Disposition', f'attachment; filename="{filename}"')
            ]
            
            return request.make_response(pdf_content, headers=pdfhttpheaders)
            
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error("Error generating payslip PDF for payslip %s: %s", payslip_id, str(e))
            _logger.exception("Full traceback:")
            return request.redirect(MY_EMPLOYEE_URL + '/payslips?error=pdf_generation_failed')

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

    @http.route(MY_EMPLOYEE_URL + '/leaves', type='http', auth='user', website=True)
    def portal_leave_history(self, **kwargs):
        employee = request.env[HR_EMPLOYEE_MODEL].sudo().search([('user_id', '=', request.uid)], limit=1)
        domain = [('employee_id', '=', employee.id)]
        
        # Filtering logic
        status = kwargs.get('status')
        if status:
            if status == 'all':
                pass  # Show all statuses
            else:
                domain += [('state', '=', status)]
        
        leave_type = kwargs.get('leave_type')
        if leave_type:
            domain += [('holiday_status_id', '=', int(leave_type))]
        
        year = kwargs.get('year')
        if year:
            try:
                year = int(year)
                domain += [('date_from', '>=', f'{year}-01-01'), ('date_from', '<=', f'{year}-12-31')]
            except (ValueError, TypeError):
                pass
        
        leave_requests = request.env['hr.leave'].sudo().search(domain, order='date_from desc', limit=50)
        
        # For filter dropdowns
        from datetime import datetime
        current_year = datetime.now().year
        years = list(range(current_year, current_year - 3, -1))
        leave_types = request.env['hr.leave.type'].sudo().search([('active', '=', True)])
        
        # Calculate leave balances for current employee
        leave_balances = []
        for leave_type_rec in leave_types:
            allocation = request.env['hr.leave.allocation'].sudo().search([
                ('employee_id', '=', employee.id),
                ('holiday_status_id', '=', leave_type_rec.id),
                ('state', '=', 'validate')
            ], limit=1)
            
            # Calculate used leaves for this type
            used_leaves = sum(request.env['hr.leave'].sudo().search([
                ('employee_id', '=', employee.id),
                ('holiday_status_id', '=', leave_type_rec.id),
                ('state', '=', 'validate')
            ]).mapped('number_of_days'))
            
            allocated_days = allocation.number_of_days if allocation else 0
            remaining_days = allocated_days - used_leaves
            
            leave_balances.append({
                'leave_type': leave_type_rec,
                'allocated': allocated_days,
                'used': used_leaves,
                'remaining': remaining_days
            })
        
        return request.render('employee_self_service_portal.portal_leaves', {
            'leave_requests': leave_requests,
            'employee': employee,
            'leave_types': leave_types,
            'leave_balances': leave_balances,
            'years': years,
            'selected_status': status or '',
            'selected_leave_type': leave_type or '',
            'selected_year': year or '',
        })

    @http.route(MY_EMPLOYEE_URL + '/leaves/request', type='http', auth='user', website=True, methods=['GET', 'POST'])
    def portal_leave_request(self, **post):
        employee = request.env[HR_EMPLOYEE_MODEL].sudo().search([('user_id', '=', request.uid)], limit=1)
        leave_types = request.env['hr.leave.type'].sudo().search([('active', '=', True)])
        
        error = None
        success = None
        
        if request.httprequest.method == 'POST':
            holiday_status_id = post.get('holiday_status_id')
            date_from = post.get('date_from')
            date_to = post.get('date_to')
            description = post.get('description')
            
            if not (holiday_status_id and date_from and date_to):
                error = 'All required fields must be filled.'
            else:
                try:
                    # Convert date strings to proper format for Odoo
                    from datetime import datetime
                    import logging
                    _logger = logging.getLogger(__name__)
                    
                    # Log the received dates for debugging
                    _logger.info("Leave Request Debug: Received date_from='%s', date_to='%s'", date_from, date_to)
                    
                    # Parse the date strings - keep as date objects, not datetime
                    date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                    date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                    
                    # Also create datetime objects for compatibility
                    datetime_from = datetime.strptime(date_from, '%Y-%m-%d')
                    datetime_to = datetime.strptime(date_to, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
                    
                    _logger.info("Leave Request Debug: Parsed date_from_obj='%s', date_to_obj='%s'", date_from_obj, date_to_obj)
                    
                    # Use both field naming conventions to ensure compatibility
                    vals = {
                        'employee_id': employee.id,
                        'holiday_status_id': int(holiday_status_id),
                        'request_date_from': date_from_obj,         # Main field for from date
                        'request_date_to': date_to_obj,             # Main field for to date
                        'date_from': datetime_from,                 # Legacy datetime field
                        'date_to': datetime_to,                     # Legacy datetime field
                        'name': description or 'Leave Request',
                        'state': 'confirm',  # Set to confirm state for approval
                        'request_unit_hours': False,                # Ensure we're requesting full days
                    }
                    
                    _logger.info("Leave Request Debug: Creating leave with vals: %s", vals)
                    
                    # Create leave request
                    leave_request = request.env['hr.leave'].sudo().create(vals)
                    
                    # Log the created leave request details
                    _logger.info("Leave Request Debug: Created leave ID=%s, request_date_from='%s', request_date_to='%s', date_from='%s', date_to='%s'", 
                                leave_request.id, leave_request.request_date_from, leave_request.request_date_to,
                                leave_request.date_from, leave_request.date_to)
                    
                    success = 'Leave request submitted successfully and is pending approval.'
                    
                    # Redirect to leave history to avoid resubmission
                    return request.redirect(MY_EMPLOYEE_URL + '/leaves?message=' + success)
                except Exception as e:
                    error = f'Error submitting leave request: {str(e)}'
        
        return request.render('employee_self_service_portal.portal_leave_request', {
            'employee': employee,
            'leave_types': leave_types,
            'error': error,
            'success': success,
        })

    @http.route(MY_EMPLOYEE_URL + '/leaves/cancel/<int:leave_id>', type='http', auth='user', website=True, methods=['POST'])
    def portal_leave_cancel(self, leave_id, **post):
        employee = request.env[HR_EMPLOYEE_MODEL].sudo().search([('user_id', '=', request.uid)], limit=1)
        leave_request = request.env['hr.leave'].sudo().search([
            ('id', '=', leave_id),
            ('employee_id', '=', employee.id)
        ], limit=1)
        
        # Only allow cancellation if leave is in draft or confirm state
        if leave_request and leave_request.state in ['draft', 'confirm']:
            try:
                # Try different methods for cancellation
                if hasattr(leave_request, 'action_refuse'):
                    leave_request.action_refuse()
                elif hasattr(leave_request, 'action_cancel'):
                    leave_request.action_cancel()
                else:
                    # Fallback: directly set state to cancel
                    leave_request.write({'state': 'cancel'})
            except Exception:
                # Fallback: directly set state to cancel
                leave_request.write({'state': 'cancel'})
        
        return request.redirect(MY_EMPLOYEE_URL + '/leaves')

    @http.route(MY_EMPLOYEE_URL + '/leaves/view/<int:leave_id>', type='http', auth='user', website=True)
    def portal_leave_view(self, leave_id, **kwargs):
        employee = request.env[HR_EMPLOYEE_MODEL].sudo().search([('user_id', '=', request.uid)], limit=1)
        leave_request = request.env['hr.leave'].sudo().search([
            ('id', '=', leave_id),
            ('employee_id', '=', employee.id)
        ], limit=1)
        
        if not leave_request:
            return request.redirect(MY_EMPLOYEE_URL + '/leaves')
        
        return request.render('employee_self_service_portal.portal_leave_view', {
            'leave_request': leave_request,
            'employee': employee,
        })

    def _get_leave_balance_data(self, employee):
        """Helper method to get leave balance information"""
        leave_types = request.env['hr.leave.type'].sudo().search([
            ('active', '=', True),
            ('request_unit', 'in', ['day', 'hour'])
        ])
        
        balance_data = []
        for leave_type in leave_types:
            # Get current year allocations
            current_year = fields.Date.today().year
            start_date = fields.Date.from_string(f'{current_year}-01-01')
            end_date = fields.Date.from_string(f'{current_year}-12-31')
            
            # Get allocations
            allocations = request.env['hr.leave.allocation'].sudo().search([
                ('employee_id', '=', employee.id),
                ('holiday_status_id', '=', leave_type.id),
                ('state', '=', 'validate'),
                ('date_from', '<=', end_date),
                ('date_to', '>=', start_date),
            ])
            
            # Get used/requested leaves
            used_leaves = request.env['hr.leave'].sudo().search([
                ('employee_id', '=', employee.id),
                ('holiday_status_id', '=', leave_type.id),
                ('state', 'in', ['validate', 'validate1']),
                ('date_from', '>=', start_date),
                ('date_to', '<=', end_date),
            ])
            
            # Get pending leaves
            pending_leaves = request.env['hr.leave'].sudo().search([
                ('employee_id', '=', employee.id),
                ('holiday_status_id', '=', leave_type.id),
                ('state', 'in', ['confirm', 'validate1']),
                ('date_from', '>=', start_date),
                ('date_to', '<=', end_date),
            ])
            
            allocated = sum(allocations.mapped('number_of_days'))
            used = sum(used_leaves.mapped('number_of_days'))
            pending = sum(pending_leaves.mapped('number_of_days'))
            balance = allocated - used - pending
            
            balance_data.append({
                'leave_type': leave_type,
                'allocated': allocated,
                'used': used,
                'pending': pending,
                'balance': balance,
                'unit': leave_type.request_unit,
            })
        
        return balance_data
