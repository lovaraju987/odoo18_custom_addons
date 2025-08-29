{
    "name": "Employee Attendance View",
    "version": "18.0.1.0.0",
    "category": "Human Resources",
    "summary": "View employee attendances directly from employee form",
    "description": """
        This module adds a new notebook page in the employee form to view
        attendance records directly from the employee profile.
        
        Features:
        - View attendance records in employee form
        - Filter by date range
        - See check-in and check-out times, work hours and status
    """,
    "author": "Lovaraju Mylapalli",
    "website": "https://www.mlr.com",
    "license": "LGPL-3",
    "depends": ["hr", "hr_attendance"],
    "data": [
        "views/hr_employee_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
