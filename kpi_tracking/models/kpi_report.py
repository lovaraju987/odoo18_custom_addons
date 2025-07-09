# Your KPI model logic goes here
from odoo import models, fields, api
from lxml import etree
from datetime import timedelta, datetime, time
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
from collections import namedtuple
from types import SimpleNamespace

# Constants for model names
KPI_REPORT_SUBMISSION_MODEL = 'kpi.report.submission'
KPI_REPORT_GROUP_MODEL = 'kpi.report.group'
KPI_REPORT_GROUP_SUBMISSION_MODEL = 'kpi.report.group.submission'

class KPIReport(models.Model):
    _name = 'kpi.report'
    _inherit = ['mail.thread']
    _description = 'KPI Report'
    _order = 'department, name'

    # SQL constraints for data integrity
    _sql_constraints = [
        ('target_value_positive', 'CHECK(target_value >= 0)', 'Target value must be positive or zero'),
        ('achievement_percent_range', 'CHECK(achievement_percent >= 0)', 'Achievement percent cannot be negative'),
        ('unique_kpi_name_report', 'UNIQUE(name, report_id)', 'KPI name must be unique within a report group'),
    ]

    count_a = fields.Integer(string="Base Count (count_a)", readonly=True)
    count_b = fields.Integer(string="Filtered Count (count_b)", readonly=True)
    name = fields.Char(string='KPI Name', required=True)
    report_id = fields.Many2one('kpi.report.group', string="Report")
    kpi_type = fields.Selection([('manual', 'Manual'), ('auto', 'Auto')], required=True)
    assigned_user_ids = fields.Many2many('res.users', string="Assigned Users")
    target_type = fields.Selection([
        ('number', 'Number'),
        ('percent', 'Percentage'),
        ('currency', '₹ Rupees'),
        ('boolean', 'Achieved / Not Achieved'),
        ('duration', 'Time (hrs)')
    ], string="Target Type", default='number')

    target_value = fields.Float(string="Target Value")
    target_unit_display = fields.Char(
        compute="_compute_target_unit_display",
        string="Target (with Unit)",
        store=False
    )
    priority_weight = fields.Selection([
            ('1', 'Very Low'),
            ('2', 'Low'),
            ('3', 'Medium'),
            ('4', 'High'),
            ('5', 'Very High')
        ], string="Priority", default='3')
    
    score_label = fields.Char(string="Score Label", compute="_compute_score_label", store=True)
    score_color = fields.Selection([
        ('0', 'Grey'),     # default
        ('1', 'Green'),    # Excellent
        ('2', 'Blue'),     # Good
        ('3', 'Orange'),   # Average
        ('4', 'Yellow'),      # Needs Improvement
        ('5', 'Darkred'),  # Underperformance
    ], string="Score Color", compute="_compute_score_label", store=True)

    @api.depends('achievement_percent')
    def _compute_score_label(self):
        for rec in self:
            percent = rec.achievement_percent or 0.0
            if percent >= 95:
                rec.score_label = "Excellent"
                rec.score_color = '1'
            elif percent >= 80:
                rec.score_label = "Good"
                rec.score_color = '2'
            elif percent >= 70:
                rec.score_label = "Average"
                rec.score_color = '3'
            elif percent >= 50:
                rec.score_label = "Needs Improvement"
                rec.score_color = '4'
            else:
                rec.score_label = "Underperformance"
                rec.score_color = '5'

    @api.depends('target_type', 'target_value')
    def _compute_target_unit_display(self):
        for rec in self:
            if rec.target_type == 'percent':
                rec.target_unit_display = f"{rec.target_value:.2f} %"
            elif rec.target_type == 'currency':
                rec.target_unit_display = f"₹ {rec.target_value:,.2f}"
            elif rec.target_type == 'duration':
                rec.target_unit_display = f"{rec.target_value:.2f} hrs"
            elif rec.target_type == 'boolean':
                rec.target_unit_display = "Achieved" if rec.target_value else "Not Achieved"
            else:
                rec.target_unit_display = f"{rec.target_value}"

    achievement_percent = fields.Float(
        string="Target Achievement (%)",
        compute="_compute_achievement",
        store=True,
        digits=(16, 2)
    )

    kpi_direction = fields.Selection([
                    ('higher_better', 'Higher is Better'),
                    ('lower_better', 'Lower is Better'),
                ], string="KPI Direction", default='higher_better')

    @api.depends('value', 'target_value', 'target_type', 'kpi_direction')
    def _compute_achievement(self):
        for rec in self:
            rec.achievement_percent = rec._calculate_achievement_percent()

    note = fields.Text(string="Note")
    submission_ids = fields.One2many(KPI_REPORT_SUBMISSION_MODEL, 'kpi_id', string="Submission History")
    report_type = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly')
    ], string='Report Type')
    department = fields.Selection([
        ('sales', 'Sales'),
        ('technician', 'Technician'),
        ('operations', 'Operations'),
        ('store', 'Store'),
        ('marketing', 'Marketing'),
        ('hr', 'HR'),
        ('finance', 'Finance'),
        ('rnd', 'R&D'),
        ('it', 'IT'),
        ('admin', 'Admin'),
    ])

    @api.onchange('report_id')
    def _onchange_report_id(self):
        if self.report_id and self.report_id.department:
            self.department = self.report_id.department

    manual_value = fields.Float(string="Manual Input Value")
    value = fields.Float(string='Latest Value', readonly=True)
    last_submitted = fields.Date(string='Last Submitted')

    source_model_id = fields.Many2one('ir.model', string='Source Model')
    source_model = fields.Char(related='source_model_id.model', store=True, readonly=True)
    filter_field = fields.Char()
    filter_type = fields.Selection([
        ('today', 'Today'),
        ('this_week', 'This Week'),
        ('this_month', 'This Month')
    ])
    count_field = fields.Char()
    formula_field = fields.Text()
    source_domain = fields.Char()
    domain_test_result = fields.Char(readonly=True)
    formula_notes = fields.Text()

    @api.onchange('source_model_id')
    def _onchange_source_model_id(self):
        self.domain_test_result = ''
        if self.source_model_id:
            try:
                # Test if model can be accessed
                self.env[self.source_model_id.model].check_access_rights('read')
                self.formula_notes = "Model loaded successfully"
            except Exception as e:
                self.formula_notes = f"Error loading model: {e}"

    def action_test_domain(self):
        self.ensure_one()
        try:
            local_vars = {
                'uid': self.env.uid,
                'user': self.env.user,
                'assigned_user': self.env.user,
                'today': fields.Date.today(),
                'yesterday': fields.Date.today() - timedelta(days=1),
                'datetime': fields.Datetime,
            }
            dummy_record = SimpleNamespace()
            local_vars['record'] = dummy_record

            domain = eval(self.source_domain or '[]', {}, local_vars)

            if not self.source_model:
                self.domain_test_result = "Invalid: Source Model not defined"
                return

            count = self.env[self.source_model].search_count(domain)
            self.domain_test_result = f"Valid domain. {count} records."
        except Exception as e:
            self.domain_test_result = f"Invalid: {str(e)}"

    def action_manual_refresh_kpi(self):
        """Enhanced with permission checks"""
        self.ensure_one()
        
        # Check permissions
        if not self.env.user.has_group('kpi_tracking.group_kpi_admin'):
            if not self.env.user.has_group('kpi_tracking.group_kpi_manager'):
                if self.env.user.id not in self.assigned_user_ids.ids:
                    raise UserError("You can only update KPIs assigned to you.")
        
        today = fields.Date.today()

        if self.kpi_type == 'manual':
            self.sudo().value = self.manual_value

            for user in self.assigned_user_ids:
                existing = self.env[KPI_REPORT_SUBMISSION_MODEL].sudo().search([
                    ('kpi_id', '=', self.id),
                    ('user_id', '=', user.id),
                    ('date', '>=', datetime.combine(today, datetime.min.time())),
                    ('date', '<', datetime.combine(today + relativedelta(days=1), datetime.min.time())),
                ], limit=1)

                vals = {
                    'kpi_id': self.id,
                    'user_id': user.id,
                    'value': self.manual_value,
                    'note': self.note,
                    'date': fields.Datetime.now(),
                }

                if existing:
                    existing.sudo().write(vals)
                else:
                    self.env[KPI_REPORT_SUBMISSION_MODEL].sudo().create(vals)

        else:
            self.sudo().scheduled_update_kpis()

    @api.model
    def scheduled_update_kpis(self):
        today = fields.Date.today()

        for rec in self.search([('kpi_type', '=', 'auto')]):
            model = self.env[rec.source_model]
            assigned_users = rec.assigned_user_ids or self.env.user

            for assigned_user in assigned_users:
                try:
                    domain_base = []
                    start_date, end_date = None, None

                    if rec.filter_type == 'today':
                        start_date = datetime.combine(today, time.min)
                        end_date = datetime.combine(today, time.max)
                    elif rec.filter_type == 'this_week':
                        start_date = datetime.combine(today - timedelta(days=today.weekday()), time.min)
                        end_date = datetime.combine(today, time.max)
                    elif rec.filter_type == 'this_month':
                        start_date = datetime.combine(today.replace(day=1), time.min)
                        end_date = datetime.combine(today, time.max)

                    if rec.filter_field and start_date and end_date:
                        domain_base += [
                            (rec.filter_field, '>=', start_date),
                            (rec.filter_field, '<=', end_date)
                        ]

                    local_vars = {
                        'uid': assigned_user.id,
                        'user': assigned_user,
                        'assigned_user': assigned_user,
                        'today': today,
                    }

                    domain_filtered = domain_base[:]
                    if rec.source_domain:
                        domain_filtered += eval(rec.source_domain, {}, local_vars)

                    count_a = model.search_count(domain_base)
                    count_b = model.search_count(domain_filtered)
                    records = model.search(domain_filtered)

                    rec.count_a = count_a
                    rec.count_b = count_b

                    value = 0.0
                    if rec.formula_field:
                        formula = rec.formula_field.strip() \
                            .replace('\u202c', '') \
                            .replace('\n', '') \
                            .replace('\r', '') \
                            .replace('\t', '') \
                            .replace("“", "\"") \
                            .replace("”", "\"")

                        local_vars.update({
                            'count_a': count_a or 1,
                            'count_b': count_b,
                            'records': records,
                        })
                        safe_globals = {"__builtins__": __builtins__}
                        try:
                            value = eval(formula, safe_globals, local_vars)
                            rec.formula_notes = f"Formula evaluated for {assigned_user.name}"
                        except Exception as e:
                            rec.formula_notes = f"Error evaluating for {assigned_user.name}: {e}"

                    rec.value = value
                    rec.last_submitted = fields.Datetime.now()

                    existing = self.env[KPI_REPORT_SUBMISSION_MODEL].sudo().search([
                        ('kpi_id', '=', rec.id),
                        ('user_id', '=', assigned_user.id),
                        ('date', '>=', datetime.combine(today, datetime.min.time())),
                        ('date', '<', datetime.combine(today + timedelta(days=1), datetime.min.time())),
                    ], limit=1)

                    vals = {
                        'kpi_id': rec.id,
                        'user_id': assigned_user.id,
                        'value': value,
                        'note': rec.note,
                        'date': fields.Datetime.now(),
                        'score_label': rec.score_label,
                        'score_color': rec.score_color,
                    }

                    if existing:
                        existing.sudo().write(vals)
                    else:
                        self.env[KPI_REPORT_SUBMISSION_MODEL].sudo().create(vals)

                except Exception as e:
                    rec.formula_notes = f"Error calculating for {assigned_user.name}: {e}"

        # === Append Group KPI Submission after all individual KPI updates ===
        group_model = self.env[KPI_REPORT_GROUP_MODEL]
        group_submission_model = self.env[KPI_REPORT_GROUP_SUBMISSION_MODEL]
        for group in group_model.search([]):
            vals = {
                'report_id': group.id,
                'value': group.group_achievement_percent,
                'user_id': self.env.uid,
                'note': 'Auto submission after KPI update',
                'date': fields.Datetime.now(),
                'score_label': group.score_label,
                'score_color': group.score_color,
            }

            existing = group_submission_model.search([
                ('report_id', '=', group.id),
                ('date', '>=', datetime.combine(today, datetime.min.time())),
                ('date', '<', datetime.combine(today + timedelta(days=1), datetime.min.time())),
            ], limit=1)

            if existing:
                existing.sudo().write(vals)
            else:
                group_submission_model.sudo().create(vals)

    @api.constrains('source_domain', 'formula_field', 'source_model')
    def _check_domain_and_formula(self):
        class DummyUser:
            def __init__(self, id):
                self.id = id

        class DummySafeNamespace(SimpleNamespace):
            def __getattr__(self, name):
                return [] if name.endswith('_ids') else 0

        for rec in self:
            if rec.source_domain:
                try:
                    local_vars = {
                        'assigned_user': DummyUser(1),
                        'today': fields.Date.today(),
                        'yesterday': fields.Date.today() - timedelta(days=1),
                        'datetime': fields.Datetime,
                    }
                    eval(rec.source_domain, {}, local_vars)
                except Exception as e:
                    raise ValidationError(f"Invalid domain syntax:\n{e}")

            if rec.formula_field:
                try:
                    dummy_records = [DummySafeNamespace() for _ in range(3)]
                    local_vars = {
                        'count_a': 100,
                        'count_b': 20,
                        'count_c': 5,
                        'records': dummy_records,
                        'assigned_user': DummyUser(1),
                        'today': fields.Date.today(),
                        'yesterday': fields.Date.today() - timedelta(days=1),
                        'datetime': fields.Datetime,
                    }
                    eval(rec.formula_field.strip(), {}, local_vars)
                except Exception as e:
                    raise ValidationError(f"Invalid formula:\n{e}")

    @api.constrains('formula_field', 'source_domain')
    def _validate_formula_security(self):
        """Validate formula for security risks"""
        for rec in self:
            rec._validate_formula_keywords()
            rec._validate_domain_keywords()

    def _validate_formula_keywords(self):
        """Check formula for dangerous keywords"""
        if self.formula_field:
            dangerous_keywords = ['import', 'exec', 'eval', '__', 'open', 'file', 'compile', 'globals']
            formula_lower = self.formula_field.lower()
            for keyword in dangerous_keywords:
                if keyword in formula_lower:
                    raise ValidationError(f"Formula contains dangerous keyword: {keyword}")

    def _validate_domain_keywords(self):
        """Check domain for dangerous keywords"""
        if self.source_domain:
            dangerous_keywords = ['import', 'exec', 'eval', '__', 'open', 'file', 'compile', 'globals']
            domain_lower = self.source_domain.lower()
            for keyword in dangerous_keywords:
                if keyword in domain_lower:
                    raise ValidationError(f"Domain contains dangerous keyword: {keyword}")

    @api.constrains('target_value', 'target_type')
    def _validate_target_value(self):
        """Validate target value based on target type"""
        for rec in self:
            if rec.target_value is not False:  # Allow 0 but not False
                if rec.target_type == 'percent' and rec.target_value > 100:
                    raise ValidationError("Percentage target cannot exceed 100%")
                if rec.target_type == 'boolean' and rec.target_value not in [0, 1]:
                    raise ValidationError("Boolean target must be 0 or 1")
                if rec.target_value < 0:
                    raise ValidationError("Target value cannot be negative")

    @api.model
    def send_manual_kpi_reminders(self):
        manual_kpis = self.search([('kpi_type', '=', 'manual')])
        template = self.env.ref('kpi_tracking.kpi_manual_entry_email_template', raise_if_not_found=False)

        if not template:
            raise UserError("Email template 'kpi_manual_entry_email_template' not found")

        for kpi in manual_kpis:
            for user in kpi.assigned_user_ids:
                template.with_context(kpi_name=kpi.name).send_mail(user.id, force_send=True)

    # Simple boolean field instead of computed field for now
    is_admin = fields.Boolean(string="Can Edit KPI", default=True, store=False)

    def _calculate_achievement_percent(self):
        """Calculate achievement percentage based on target type and direction"""
        if self.target_type in ['number', 'percent', 'currency', 'duration']:
            return self._calculate_numeric_achievement()
        elif self.target_type == 'boolean':
            return 100.0 if self.value else 0.0
        else:
            return 0.0

    def _calculate_numeric_achievement(self):
        """Calculate achievement for numeric target types"""
        if self.kpi_direction == 'higher_better':
            return (self.value / self.target_value * 100) if self.target_value else 0.0
        elif self.kpi_direction == 'lower_better':
            if self.value == 0:
                return 100.0
            else:
                ratio = (self.target_value / self.value * 100) if self.value else 0.0
                return min(ratio, 100.0)
        return 0.0
