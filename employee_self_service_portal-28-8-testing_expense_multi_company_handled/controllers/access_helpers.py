# controllers/access_helpers.py
from odoo import http
from odoo.http import request
import werkzeug


def check_portal_access(feature_name):
    """
    Decorator to check if the current portal user has access to a specific feature.
    
    Args:
        feature_name (str): The name of the feature to check access for. 
                           Should be one of: 'crm', 'attendance', 'expenses', 'payslip'
    
    Returns:
        decorator: Function wrapper that checks access before allowing method execution
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Skip check for admin/internal users
            if request.env.user.has_group('base.group_user'):
                return func(*args, **kwargs)
            
            # Get the employee record for the current user
            employee = request.env['hr.employee'].sudo().search([('user_id', '=', request.uid)], limit=1)
            
            # Check if employee has access to the feature
            access_field = f'portal_access_{feature_name}'
            if not employee or not hasattr(employee, access_field) or not getattr(employee, access_field):
                # No access - redirect to main portal page with warning
                return request.redirect('/my?access_error=1')
            
            # User has access - proceed with the original method
            return func(*args, **kwargs)
            
        return wrapper
    return decorator


def has_feature_access(feature_name):
    """
    Check if the current user has access to a specific feature.
    
    Args:
        feature_name (str): The name of the feature to check access for.
                           Should be one of: 'crm', 'attendance', 'expenses', 'payslip'
    
    Returns:
        bool: True if the user has access, False otherwise
    """
    # Admin/internal users always have access
    if request.env.user.has_group('base.group_user'):
        return True
        
    # Get the employee record for the current user
    employee = request.env['hr.employee'].sudo().search([('user_id', '=', request.uid)], limit=1)
    
    # Check if employee has access to the feature
    access_field = f'portal_access_{feature_name}'
    if not employee or not hasattr(employee, access_field) or not getattr(employee, access_field):
        return False
    
    return True
