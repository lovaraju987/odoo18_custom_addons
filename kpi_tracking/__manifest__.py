{
    "name": "KPI Tracking & Performance Management",
    "version": "18.1.0",
    "summary": "Advanced KPI tracking with automated calculations, reporting, and performance analytics",
    "description": """
KPI Tracking & Performance Management System
============================================

A comprehensive performance management solution for tracking, monitoring, and evaluating Key Performance Indicators (KPIs) across different departments.

Key Features:
• Manual and Automatic KPI tracking
• Department-wise organization and reporting
• Formula-based calculations from any Odoo model
• Target achievement tracking with visual indicators
• Email reminders and automated notifications
• Historical submission tracking and audit trails
• Role-based access control (Admin/Manager/User)
• Dashboard views with progress bars and color coding
• CRON-based automated updates

Target Types Supported:
• Number values
• Percentage calculations
• Currency amounts (₹)
• Boolean achievements
• Time duration (hours)

Perfect for businesses wanting to:
• Track sales performance and targets
• Monitor operational efficiency
• Measure employee productivity
• Evaluate departmental performance
• Maintain performance audit trails

Compatible with Odoo 18 Community and Enterprise editions.
    """,
    "author": "OneTo7 Solutions",
    "website": "https://www.oneto7solutions.in",
    "support": "info@oneto7solutions.in",
    "category": "Human Resources",
    "license": "OPL-1",
    "price": 20.00,
    "currency": "USD",
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
    "demo": [
        "demo/demo_data.xml",
    ],
    "images": [
        "static/description/banner.png",
        "static/description/icon.png",
        "static/description/kpi_dashboard.png",
        "static/description/kpi_form.png",
        "static/description/kpi_reports.png",
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
    "sequence": 1,
}
