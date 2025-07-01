# -*- coding: utf-8 -*-
{
    "name": "Employee Project Allocation",
    "version": "1.0",
    "category": "Project",
    "summary": "Add allocation % to projects and restrict timesheets by allocation and daily limits.",
    "description": "Restricts employee timesheets based on project allocation percentage and max hours per day.",
    "author": "OneTo7 Services",
    "license": "LGPL-3",
    "depends": ["project", "hr_timesheet", "sale_timesheet"],
    "data": [
        "views/project_project_views.xml",
        "views/employee_allocation_views.xml",
    ],
    "installable": True,
    "application": False,
}
