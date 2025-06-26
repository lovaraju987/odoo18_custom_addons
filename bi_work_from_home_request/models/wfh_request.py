# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from collections import namedtuple, defaultdict
from odoo.tools import float_compare, format_date
from odoo.addons.resource.models.utils import float_to_time, HOURS_PER_DAY
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime, time, date, timedelta
from pytz import timezone, UTC
import pytz
import calendar
from odoo.osv import expression


DummyAttendance = namedtuple('DummyAttendance', 'hour_from, hour_to, dayofweek, day_period, week_type')

 
class WFHRequest(models.Model):
    _name = 'wfh.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Work From Home Request'
    _rec_name = 'name'

    def _get_default_emp(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)

    name = fields.Char(string="Description", tracking=True)
    employee_id = fields.Many2one('hr.employee', "Employee", tracking=True, default=_get_default_emp)
    wfh_type_id = fields.Many2one('wfh.type', "Work From Home Type", tracking=True)
    request_date_from = fields.Date(string="Date From", tracking=True,default=fields.date.today(),)
    request_date_to = fields.Date(string="Date To", tracking=True,default=fields.date.today(),)
    number_of_days_display = fields.Float(string="Duration", compute="compute_number_of_day",store=True, copy=False,)
    state = fields.Selection([('draft', 'Submit'), ('confirm', 'To Approve'), ('approve', 'Approved'), ('approve1', 'Second Approval'),('refuse', 'Refused')],
                             compute='_compute_wfh_state', store=True, tracking=True, copy=False, readonly=False)
    manager_id = fields.Many2one(string="Manager", related='wfh_type_id.user_id')
    is_manager = fields.Boolean(string="Is Manager?", compute="compute_is_manager")
    all_employee_ids = fields.Many2many('hr.employee', compute='_compute_all_wfh_employees', compute_sudo=True)
    validation_type = fields.Selection(string='Validation Type', related='wfh_type_id.approval', readonly=False)
    user_id = fields.Many2one('res.users', string='User', related='employee_id.user_id', related_sudo=True, compute_sudo=True, store=True, readonly=True, index=True)
    employee_company_id = fields.Many2one(related='employee_id.company_id', readonly=True, store=True)
    active_employee = fields.Boolean(related='employee_id.active', string='Employee Active', readonly=True)
    date_from = fields.Datetime(
        'Start Date', compute='_compute_date_from_to', store=True, readonly=False, index=True, copy=False, tracking=True)
    date_to = fields.Datetime(
        'End Date', compute='_compute_date_from_to', store=True, readonly=False, copy=False, tracking=True)
    is_manager_id = fields.Boolean( compute="_compute_is_manager" ,store=False)    

    @api.depends_context('uid')
    def _compute_is_manager(self):
        for request in self:
            request.is_manager_id = request.user_id and request.user_id.has_group('hr_holidays.group_hr_holidays_manager')

    def search_fetch(self, domain, field_names, offset=0, limit=None, order=None):
        domain = domain or []
        
        if self.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
            domain.append(('user_id.groups_id', 'in', [self.env.ref('hr_holidays.group_hr_holidays_manager').id]))
        else:
            domain.append(('user_id', '=', self.env.user.id))
        return super().search_fetch(domain, field_names, offset=offset, limit=limit, order=order)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        domain = domain or []
        if self.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
            domain.append(('user_id.groups_id', 'in', [self.env.ref('hr_holidays.group_hr_holidays_manager').id]))
        else:
            domain.append(('user_id', '=', self.env.user.id))
        return super().read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

    @api.model_create_multi
    def create(self, vals_list):
        res = super(WFHRequest,self).create(vals_list)
        for holiday in res:
            holiday_sudo = holiday.sudo()
            holiday_sudo.action_submit()
        return res

    @api.depends('wfh_type_id')
    def _compute_display_name(self):
        for request in self:
            request.display_name = _(' %s Work From Home Request: %s Days On %s.') % (request.employee_id.name, request.number_of_days_display, request.request_date_from)

    @api.depends('wfh_type_id')
    def _compute_wfh_state(self):
        for leave in self:
            leave.state = 'confirm'

    @api.depends('employee_id')
    def _compute_all_wfh_employees(self):
        for leave in self:
            leave.all_employee_ids = leave.employee_id

    @api.onchange('wfh_type_id')
    def onchange_wfh_type_id(self):
        for rec in self:
            wfh_request_ids = self.search(
                [('wfh_type_id', '=', rec.wfh_type_id.id), ('employee_id', '=', rec.employee_id.id),
                 ('id', '!=', self._origin.id), ('state', '=', 'approve')])

    @api.depends('state','request_date_from','request_date_to')
    def compute_is_manager(self):
        for rec in self:
            find_manger_id = self.employee_id.parent_id.user_id
            if rec.validation_type == 'by_officer':
                if rec.state == 'confirm':
                    if self.env.user == find_manger_id:
                        rec.is_manager = True
                    else:
                        rec.is_manager = False
                elif rec.state == 'approve1':
                    if rec.manager_id == self.env.user:
                        rec.is_manager = True
                    else:
                        rec.is_manager = False
                else:
                    if self.env.user == find_manger_id:
                        rec.is_manager = True
                    else:
                        rec.is_manager = False
            else:
                if self.env.user == find_manger_id:
                    rec.is_manager = True
                else:
                    rec.is_manager = False

    @api.depends('request_date_from','request_date_to')
    def compute_number_of_day(self):
        for rec in self:
            if rec.request_date_from and rec.request_date_to:
                rec.number_of_days_display = ((rec.request_date_to - rec.request_date_from).days + 1)
            else:
                rec.number_of_days_display = 0

    @api.depends('request_date_from', 'request_date_to','employee_id','wfh_type_id')
    def _compute_date_from_to(self):
        for holiday in self:
            attendance_from, attendance_to = holiday._get_attendances(holiday.employee_id, holiday.request_date_from, holiday.request_date_to)
            compensated_request_date_from = holiday.request_date_from
            compensated_request_date_to = holiday.request_date_to

            hour_from = attendance_from.hour_from
            hour_to = attendance_to.hour_to

            holiday.date_from = self._get_start_or_end_from_attendance(hour_from, compensated_request_date_from, holiday.employee_id or holiday)
            holiday.date_to = self._get_start_or_end_from_attendance(hour_to, compensated_request_date_to, holiday.employee_id or holiday)
    

    @api.constrains('request_date_from', 'request_date_to', 'employee_id','wfh_type_id')
    def _check_date(self):
        all_wfh_employees = self.all_employee_ids
        all_wfh_leaves = self.search([
            ('date_from', '<', max(self.mapped('date_to'))),
            ('date_to', '>', min(self.mapped('date_from'))),
            ('employee_id', 'in', all_wfh_employees.ids),
            ('id', 'not in', self.ids),
        ])

        for holiday in self:
            find_request = self.env['wfh.request'].search([('employee_id','=',holiday.employee_id.id),('state','in',['confirm','approve','approve1'])])
            start_date = self.request_date_from.replace(day=1)
            last_date = self.request_date_from.replace(day=calendar.monthrange(self.request_date_from.year, self.request_date_from.month)[1])
            current_month = datetime.now().month
            current_year = datetime.now().year
            for rec in find_request:
                start_dateq = self.request_date_from.replace(day=1)
                last_dateq = self.request_date_from.replace(
                    day=calendar.monthrange(self.request_date_from.year, self.request_date_from.month)[1])
                total_days = (last_dateq - start_dateq).days + 1
                month_day=find_request.filtered(lambda x:x.request_date_from > start_dateq and x.request_date_from < last_dateq)
                if month_day:
                    current_day = sum(month_day.mapped('number_of_days_display'))
                    if current_day > holiday.wfh_type_id.monthly_limit:
                        raise ValidationError(
                            _("Your monthly Work From Home limit has been reached. You are unable to create additional Work From Home requests for this month"))

            if holiday.request_date_from  < date.today():
                raise UserError(_("You Can Not Create Past Day Work From Home Request"))
            else:
                domain = [
                    ('date_from', '<', holiday.date_to),
                    ('date_to', '>', holiday.date_from),
                    ('id', '!=', holiday.id),
                    ('state', 'not in', ['refuse']),
                ]

                employee_ids = (holiday.employee_id).ids
                search_domain = domain + [('employee_id', 'in', employee_ids)]
                conflicting_holidays = all_wfh_leaves.filtered_domain(search_domain)

                if conflicting_holidays:
                    conflicting_holidays_list = []
                    # Do not display the name of the employee if the conflicting holidays have an employee_id.user_id equivalent to the user id
                    holidays_only_have_uid = bool(holiday.employee_id)
                    holiday_states = dict(conflicting_holidays.fields_get(allfields=['state'])['state']['selection'])
                    for conflicting_holiday in conflicting_holidays:
                        conflicting_holiday_data = {}
                        conflicting_holiday_data['employee_name'] = conflicting_holiday.employee_id.name
                        conflicting_holiday_data['date_from'] = format_date(self.env, min(conflicting_holiday.mapped('date_from')))
                        conflicting_holiday_data['date_to'] = format_date(self.env, min(conflicting_holiday.mapped('date_to')))
                        conflicting_holiday_data['state'] = holiday_states[conflicting_holiday.state]
                        if conflicting_holiday.employee_id.user_id.id != self.env.uid:
                            holidays_only_have_uid = False
                        if conflicting_holiday_data not in conflicting_holidays_list:
                            conflicting_holidays_list.append(conflicting_holiday_data)
                    if not conflicting_holidays_list:
                        return
                    conflicting_holidays_strings = []
                    if holidays_only_have_uid:
                        for conflicting_holiday_data in conflicting_holidays_list:
                            conflicting_holidays_string = _('From %(date_from)s To %(date_to)s - %(state)s',
                                                            date_from=conflicting_holiday_data['date_from'],
                                                            date_to=conflicting_holiday_data['date_to'],
                                                            state=conflicting_holiday_data['state'])
                            conflicting_holidays_strings.append(conflicting_holidays_string)
                        raise ValidationError(_('You can not set two work from home request that overlap on the same day.\nExisting time off:\n%s') %
                                              ('\n'.join(conflicting_holidays_strings)))

    def copy_data(self, default=None):
        raise UserError(_('A Work From Home Request Cannot Be Duplicated.'))

    def unlink(self):
        error_message = _('You cannot delete a time off which is in %s state')
        state_description_values = {elem[0]: elem[1] for elem in self._fields['state']._description_selection(self.env)}
        for holiday in self.filtered(lambda holiday: holiday.state not in ['draft', 'confirm']):
                raise UserError(error_message % (state_description_values.get(holiday.state),))
        for holiday in self.filtered(lambda holiday: holiday.state  in ['draft', 'confirm']):
            return super(WFHRequest,self).unlink()

    def action_submit(self):
        for rec in self:
            note = _(
                'New %(leave_type)s Work From Request created by %(user)s',
                leave_type=rec.wfh_type_id.name,
                user=rec.employee_id.name,
            )
            rec.state = 'confirm'
            rec.activity_update()

    def action_approve(self):
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': None,
                'type': None,
                'sticky': False,
            },
        }
        for rec in self:
            find_manger_id = self.employee_id.parent_id.user_id or self.employee_id.timesheet_manager_id
            if rec.validation_type == 'by_officer':
                if self.env.user.id == find_manger_id.id:
                    rec.state = 'approve1'
                    rec.activity_update()
                    rec.message_post(
                        body=_(
                            'Your work from home request planned on %(date)s has been accepted',
                            leave_type=rec.wfh_type_id.name,
                            date=rec.request_date_from
                        ),
                        partner_ids=rec.employee_id.user_id.partner_id.ids)
                else:
                    notification['params'].update({
                        'message': _('You cannot approve the work from home request as they either belong to employees who are not part of your team'),
                        'type': 'warning',
                    })
                    return notification
            else:
                if self.env.user.id == find_manger_id.id:
                    rec.state = 'approve'
                    rec.activity_update()
                    rec.message_post(
                        body=_(
                            'Your work from home request planned on %(date)s has been accepted',
                            leave_type=rec.wfh_type_id.name,
                            date=rec.request_date_from
                        ),
                        partner_ids=rec.employee_id.user_id.partner_id.ids)
                else:
                    notification['params'].update({
                        'message': _('You cannot approve the work from home request as they either belong to employees who are not part of your team'),
                        'type': 'warning',
                    })
                    return notification                

    def action_validate(self):
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': None,
                'type': None,
                'sticky': False,
            },
        }
        for rec in self:
            if rec.validation_type == 'by_officer':
                if self.env.user.id == rec.wfh_type_id.user_id.id:
                    rec.state = 'approve'
                    rec.activity_update()
                else:
                    notification['params'].update({
                            'message': _('You cannot approve the work-from-home request because you are not the designated Time Off Officer for work from home type "%s".') % rec.wfh_type_id.name,                            
                            'type': 'warning',
                        })
                    return notification

    def action_refuse(self):
        for rec in self:
            rec.state = 'refuse'
            rec.message_post(
                body=_(
                    'Your work from home request planned on %(date)s has been refused',
                    leave_type=rec.wfh_type_id.name,
                    date=rec.request_date_from
                ),
                partner_ids=rec.employee_id.user_id.partner_id.ids)

            rec.activity_update()

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    def activity_update(self):
        to_clean, to_do = self.env['wfh.request'], self.env['wfh.request']
        for holiday in self:
            note = _(
                'New %(leave_type)s Work From Request created by %(user)s',
                leave_type=holiday.wfh_type_id.name,
                user=holiday.employee_id.name,
            )
            if holiday.state == 'draft':
                to_clean |= holiday
            elif holiday.state == 'confirm':
                holiday.with_context(short_name=False).activity_schedule(
                    'bi_work_from_home_request.mail_activity_wfh_req',
                    note=note,
                    user_id=holiday.sudo()._get_responsible_for_approval().id or self.env.user.id)
            elif holiday.state == 'approve1':
                holiday.activity_feedback(['bi_work_from_home_request.mail_activity_wfh_req'])
                holiday.with_context(short_name=False).activity_schedule(
                    'hr_holidays.mail_act_leave_second_approval',
                    note=note,
                    user_id=holiday.sudo()._get_responsible_for_approval().id or self.env.user.id)
            elif holiday.state == 'approve':
                to_do |= holiday
            elif holiday.state == 'refuse':
                to_clean |= holiday
        if to_clean:
            to_clean.activity_unlink(['bi_work_from_home_request.mail_activity_wfh_req', 'hr_holidays.mail_act_leave_second_approval'])
        if to_do:
            to_do.activity_feedback(['bi_work_from_home_request.mail_activity_wfh_req', 'hr_holidays.mail_act_leave_second_approval'])

    def _get_responsible_for_approval(self):
        self.ensure_one()

        responsible = self.env.user

        if self.validation_type == 'by_officer':
            if  self.state == 'approve1':
                responsible = self.wfh_type_id.user_id
            else:
                responsible =  self.employee_id.leave_manager_id 
        else:
            if self.employee_id.leave_manager_id:
                responsible = self.employee_id.leave_manager_id
            elif self.employee_id.parent_id.user_id:
                responsible = self.employee_id.parent_id.user_id
    
        return responsible


    def _get_start_or_end_from_attendance(self, hour, date, employee):
        hour = float_to_time(float(hour))
        holiday_tz = timezone(employee.user_id.tz or self.env.user.tz or 'UTC')
        return holiday_tz.localize(datetime.combine(date, hour)).astimezone(UTC).replace(tzinfo=None)

    def _get_attendances(self, employee, request_date_from, request_date_to):
        resource_calendar_id = employee.resource_calendar_id or self.env.company.resource_calendar_id
        domain = [('calendar_id', '=', resource_calendar_id.id), ('display_type', '=', False)]
        day_period = self.env.context.get('day_period', False)
        if day_period:
            domain += [('day_period', '=', day_period)]
        attendances = self.env['resource.calendar.attendance'].read_group(domain,
            ['ids:array_agg(id)', 'hour_from:min(hour_from)', 'hour_to:max(hour_to)',
             'week_type', 'dayofweek', 'day_period'],
            ['week_type', 'dayofweek', 'day_period'], lazy=False)

        # Must be sorted by dayofweek ASC and day_period DESC
        attendances = sorted([DummyAttendance(group['hour_from'], group['hour_to'], group['dayofweek'], group['day_period'], group['week_type']) for group in attendances], key=lambda att: (att.dayofweek, att.day_period != 'morning'))
        default_value = DummyAttendance(0, 0, 0, 'morning', False)

        if resource_calendar_id.two_weeks_calendar:
            # find week type of start_date
            start_week_type = self.env['resource.calendar.attendance'].get_week_type(request_date_from)
            attendance_actual_week = [att for att in attendances if att.week_type is False or int(att.week_type) == start_week_type]
            attendance_actual_next_week = [att for att in attendances if att.week_type is False or int(att.week_type) != start_week_type]
            # First, add days of actual week coming after date_from
            attendance_filtred = [att for att in attendance_actual_week if int(att.dayofweek) >= request_date_from.weekday()]
            # Second, add days of the other type of week
            attendance_filtred += list(attendance_actual_next_week)
            # Third, add days of actual week (to consider days that we have remove first because they coming before date_from)
            attendance_filtred += list(attendance_actual_week)
            end_week_type = self.env['resource.calendar.attendance'].get_week_type(request_date_to)
            attendance_actual_week = [att for att in attendances if att.week_type is False or int(att.week_type) == end_week_type]
            attendance_actual_next_week = [att for att in attendances if att.week_type is False or int(att.week_type) != end_week_type]
            attendance_filtred_reversed = list(reversed([att for att in attendance_actual_week if int(att.dayofweek) <= request_date_to.weekday()]))
            attendance_filtred_reversed += list(reversed(attendance_actual_next_week))
            attendance_filtred_reversed += list(reversed(attendance_actual_week))

            # find first attendance coming after first_day
            attendance_from = attendance_filtred[0]
            # find last attendance coming before last_day
            attendance_to = attendance_filtred_reversed[0]
        else:
            # find first attendance coming after first_day
            attendance_from = next((att for att in attendances if int(att.dayofweek) >= request_date_from.weekday()), attendances[0] if attendances else default_value)
            # find last attendance coming before last_day
            attendance_to = next((att for att in reversed(attendances) if int(att.dayofweek) <= request_date_to.weekday()), attendances[-1] if attendances else default_value)

        return (attendance_from, attendance_to)

