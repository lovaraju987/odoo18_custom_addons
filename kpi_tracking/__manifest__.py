{
    "name": "KPI Tracking & Performance Management",
    "version": "18.1.0",
    "summary": "Advanced KPI tracking with automated calculations, reporting, and performance analytics",
    "description": """
KPI Tracking & Performance Management System
============================================

A comprehensive performance management solution for tracking, monitoring, and evaluating Key Performance Indicators (KPIs) across different departments.

✨ KEY FEATURES:
• Manual and Automatic KPI tracking with step-by-step guidance
• Department-wise organization and reporting
• Formula-based calculations from any Odoo model
• Target achievement tracking with visual indicators
• Email reminders and automated notifications
• Historical submission tracking and audit trails
• Role-based access control (Admin/Manager/User)
• Dashboard views with progress bars and color coding
• CRON-based automated updates

🎯 TARGET TYPES SUPPORTED:
• Number values
• Percentage calculations  
• Currency amounts (₹)
• Boolean achievements
• Time duration (hours)

📚 COMPREHENSIVE USER GUIDANCE:
• 5-minute quick setup guide (printable card)
• Step-by-step "Your First KPI" tutorial
• Role-based instructions (Admin/Manager/User)
• Department-specific KPI templates and examples
• Formula reference with real-world examples
• Troubleshooting guide and FAQ section
• Practice exercises and training materials
• Complete user manual with video tutorial outlines

🔧 FORMULA EXAMPLES INCLUDED:
• Sales Orders Count: count_a from sale.order
• Revenue Calculation: sum(record.amount_total for record in records)
• Lead Conversion: (count_b / count_a) * 100 if count_a > 0 else 0
• Employee Retention: Auto calculation from hr.employee
• Process Efficiency: Manual entry with validation

🏢 DEPARTMENT-READY TEMPLATES:
• Sales: Monthly Revenue, Lead Conversion, Customer Satisfaction
• HR: Training Completion, Employee Retention, Recruitment Time
• Operations: Process Efficiency, Cost Reduction, Quality Score
• Marketing: Campaign ROI, Lead Generation, Brand Awareness

📖 PROFESSIONAL DOCUMENTATION:
• Complete user manual (USER_MANUAL.md)
• Quick setup guide (QUICK_SETUP_GUIDE.md)
• Comprehensive README with examples
• Demo data for immediate testing
• Email templates and automation setup
• Security and access control configuration

🎯 BEST PRACTICES INCLUDED:
• DO's: Start with 3-5 KPIs, set realistic targets, train users
• DON'Ts: Too many KPIs, unrealistic targets, skip reviews
• Pro tips for performance optimization
• Common pitfalls and how to avoid them

Compatible with Odoo 18 Community and Enterprise editions.

🚀 GET STARTED IN 5 MINUTES:
1. Install module (1 min)
2. Assign user roles (2 min)
3. Create KPI group (1 min)
4. Configure first KPI (1 min)
5. Submit test value (30 sec)
Ready to track performance!
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
