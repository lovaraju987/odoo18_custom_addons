/* Portal Utility Functions */
odoo.define('employee_self_service_portal.portal_utils', function (require) {
    'use strict';

    var core = require('web.core');
    var utils = require('web.utils');

    // Common utility functions for the portal
    var PortalUtils = {
        
        /**
         * Format date for display
         */
        formatDate: function(dateString) {
            if (!dateString) return '';
            var date = new Date(dateString);
            return date.toLocaleDateString();
        },

        /**
         * Calculate days between two dates
         */
        calculateDays: function(startDate, endDate) {
            if (!startDate || !endDate) return 0;
            var start = new Date(startDate);
            var end = new Date(endDate);
            var timeDiff = end.getTime() - start.getTime();
            return Math.ceil(timeDiff / (1000 * 3600 * 24)) + 1; // +1 to include both start and end dates
        },

        /**
         * Show notification message
         */
        showNotification: function(message, type) {
            type = type || 'info';
            var alertClass = 'alert-info';
            
            switch(type) {
                case 'success':
                    alertClass = 'alert-success';
                    break;
                case 'error':
                case 'danger':
                    alertClass = 'alert-danger';
                    break;
                case 'warning':
                    alertClass = 'alert-warning';
                    break;
            }
            
            var notification = $('<div class="alert ' + alertClass + ' alert-dismissible fade show" role="alert">' +
                message +
                '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
                '<span aria-hidden="true">&times;</span>' +
                '</button>' +
                '</div>');
            
            $('.o_portal_wrap').prepend(notification);
            
            // Auto-hide after 5 seconds
            setTimeout(function() {
                notification.fadeOut();
            }, 5000);
        },

        /**
         * Confirm action with user
         */
        confirmAction: function(message, callback) {
            if (confirm(message)) {
                callback();
            }
        },

        /**
         * Get URL parameter value
         */
        getUrlParameter: function(name) {
            var url = new URL(window.location.href);
            return url.searchParams.get(name);
        },

        /**
         * Validate form fields
         */
        validateForm: function(formSelector) {
            var form = $(formSelector);
            var isValid = true;
            var errors = [];

            // Check required fields
            form.find('input[required], select[required], textarea[required]').each(function() {
                var field = $(this);
                if (!field.val() || field.val().trim() === '') {
                    isValid = false;
                    field.addClass('is-invalid');
                    var label = form.find('label[for="' + field.attr('id') + '"]').text() || field.attr('name');
                    errors.push(label + ' is required');
                } else {
                    field.removeClass('is-invalid');
                }
            });

            // Validate email fields
            form.find('input[type="email"]').each(function() {
                var email = $(this);
                if (email.val() && !PortalUtils.isValidEmail(email.val())) {
                    isValid = false;
                    email.addClass('is-invalid');
                    errors.push('Please enter a valid email address');
                }
            });

            // Validate date fields
            form.find('input[type="date"]').each(function() {
                var dateField = $(this);
                var dateValue = dateField.val();
                if (dateValue) {
                    var minDate = dateField.attr('min');
                    var maxDate = dateField.attr('max');
                    
                    if (minDate && dateValue < minDate) {
                        isValid = false;
                        dateField.addClass('is-invalid');
                        errors.push('Date cannot be before ' + minDate);
                    }
                    
                    if (maxDate && dateValue > maxDate) {
                        isValid = false;
                        dateField.addClass('is-invalid');
                        errors.push('Date cannot be after ' + maxDate);
                    }
                }
            });

            return {
                isValid: isValid,
                errors: errors
            };
        },

        /**
         * Validate email format
         */
        isValidEmail: function(email) {
            var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return emailRegex.test(email);
        },

        /**
         * Format currency
         */
        formatCurrency: function(amount, currency) {
            currency = currency || 'USD';
            return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: currency
            }).format(amount);
        },

        /**
         * Show loading spinner
         */
        showLoading: function(element) {
            element = element || 'body';
            $(element).append('<div class="o_loading_mask"><i class="fa fa-spinner fa-spin"></i></div>');
        },

        /**
         * Hide loading spinner
         */
        hideLoading: function(element) {
            element = element || 'body';
            $(element).find('.o_loading_mask').remove();
        }
    };

    // Export the utility functions
    return PortalUtils;
});

// Show success/error messages from URL parameters
$(document).ready(function() {
    var urlParams = new URLSearchParams(window.location.search);
    var message = urlParams.get('message');
    var error = urlParams.get('error');
    
    if (message) {
        setTimeout(function() {
            odoo.define.async('employee_self_service_portal.portal_utils').then(function(PortalUtils) {
                PortalUtils.showNotification(message, 'success');
            });
        }, 100);
    }
    
    if (error) {
        setTimeout(function() {
            odoo.define.async('employee_self_service_portal.portal_utils').then(function(PortalUtils) {
                PortalUtils.showNotification(error, 'error');
            });
        }, 100);
    }
});
