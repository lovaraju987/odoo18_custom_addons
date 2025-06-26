# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
    "name": "Work From Home Request by Employee | Work from Home Approval | Track Work From Home Hours",
    "version": "18.0.0.0",
    "category": "Human Resources",
    "summary": "Employee work home home request WFH approval calculate WFH hours Employee WFH hours log Remote work policy Remote attendance Work from home time tracking HR remote work tracker work from home timesheet work from home employees work from home limit time off",
    "description": """ Work From Home (WFH) Request module enhances Odoo’s Time Off system by allowing employees to easily request and manage Work From Home (WFH) days. Organisations can create different WFH types and set up approval workflows based on managers or both managers and Time Off Officers. Employees can submit WFH requests using a user-friendly dashboard by selecting dates, WFH type, and adding a description. The system automatically calculates the duration and checks against monthly limits to prevent overuse. Once submitted, managers are instantly notified and can approve or reject the requests directly in Odoo. Employees can view the status of their requests in multiple formats like List, Calendar, Pivot, and Graph views, giving clear insights into their remote work history. This module helps streamline the WFH approval process, improve transparency, and make remote work tracking more efficient for businesses. """,
    "author": "BROWSEINFO",
    'website': "https://www.browseinfo.com/demo-request?app=bi_work_from_home_request&version=18&edition=Community",
    'depends': ['hr_holidays','hr_timesheet'],
    'data': [
        'security/ir.model.access.csv',
        'data/mail_activity.xml',
        'views/wfh_type_view.xml',
        'views/wfh_request_view.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'live_test_url': "https://www.browseinfo.com/demo-request?app=bi_work_from_home_request&version=18&edition=Community",
    "images": ['static/description/banner.gif'],
    "license": 'OPL-1',
}
