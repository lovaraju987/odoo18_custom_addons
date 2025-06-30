{
    "name": "KPI Tracking",
    "version": "18.1.0",
    "summary": "Track and manage department-wise KPIs",
    "description": "KPI Tracking system for managing department-wise key performance indicators with automated calculations and reporting. Compatible with Odoo 18.",
    "author": "Custom",
    "website": "",
    "category": "Productivity",
    "license": "LGPL-3",
    "depends": ["base", "hr", "web"],
    "data": [
        "security/security.xml",
        "security/kpi_tracking_rules.xml",
        "security/ir.model.access.csv",
        "views/kpi_views.xml",
        "views/kpi_test_views.xml",
        "views/kpi_report_group.xml",
        "views/kpi_submission.xml",
        "data/email_template.xml",
        "data/cron.xml"
    ],
    "installable": True,
    "auto_install": False
}
