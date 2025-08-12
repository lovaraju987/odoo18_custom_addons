/* Leave Request Form Enhancements */
odoo.define('employee_self_service_portal.leave_form', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var PortalUtils = require('employee_self_service_portal.portal_utils');

    publicWidget.registry.LeaveRequestForm = publicWidget.Widget.extend({
        selector: '.o_portal.leave-request-form',
        events: {
            'change input[name="date_from"]': '_onFromDateChange',
            'change input[name="date_to"]': '_onToDateChange',
            'change select[name="holiday_status_id"]': '_onLeaveTypeChange',
            'submit form': '_onFormSubmit',
        },

        /**
         * Widget initialization
         */
        start: function() {
            this._super.apply(this, arguments);
            this._updateDaysCalculation();
            this._setMinimumDates();
        },

        /**
         * Set minimum dates for date inputs
         */
        _setMinimumDates: function() {
            var today = new Date().toISOString().split('T')[0];
            // Only set minimum date, don't override existing values
            var fromInput = this.$('input[name="date_from"]');
            var toInput = this.$('input[name="date_to"]');
            
            if (!fromInput.val()) {
                fromInput.attr('min', today);
            }
            if (!toInput.val()) {
                toInput.attr('min', today);
            }
        },

        /**
         * Set minimum date for date_to when date_from changes
         */
        _onFromDateChange: function (ev) {
            var fromDate = $(ev.currentTarget).val();
            var toDateInput = this.$('input[name="date_to"]');
            
            if (fromDate) {
                toDateInput.attr('min', fromDate);
                
                // If to_date is before from_date, clear it
                var toDate = toDateInput.val();
                if (toDate && toDate < fromDate) {
                    toDateInput.val('');
                }
            }
            
            this._updateDaysCalculation();
        },

        /**
         * Validate that date_to is not before date_from
         */
        _onToDateChange: function (ev) {
            var toDate = $(ev.currentTarget).val();
            var fromDate = this.$('input[name="date_from"]').val();
            
            if (fromDate && toDate && toDate < fromDate) {
                PortalUtils.showNotification('End date cannot be before start date.', 'error');
                $(ev.currentTarget).val('');
            }
            
            this._updateDaysCalculation();
        },

        /**
         * Update days calculation display
         */
        _updateDaysCalculation: function() {
            var fromDate = this.$('input[name="date_from"]').val();
            var toDate = this.$('input[name="date_to"]').val();
            
            if (fromDate && toDate) {
                var days = PortalUtils.calculateDays(fromDate, toDate);
                this.$('.days-calculation').html('<strong>Total Days: ' + days + '</strong>');
            } else {
                this.$('.days-calculation').html('');
            }
        },

        /**
         * Show leave type information when changed
         */
        _onLeaveTypeChange: function (ev) {
            var leaveTypeSelect = $(ev.currentTarget);
            var selectedOption = leaveTypeSelect.find('option:selected');
            var leaveTypeId = leaveTypeSelect.val();
            
            // You could add AJAX call here to get more leave type details
            // For now, just show basic info if available in data attributes
            var maxDays = selectedOption.data('max-days');
            var requiresApproval = selectedOption.data('requires-approval');
            
            var infoHtml = '';
            if (maxDays) {
                infoHtml += '<small class="text-info">Maximum: ' + maxDays + ' days</small><br/>';
            }
            if (requiresApproval) {
                infoHtml += '<small class="text-warning">Requires manager approval</small>';
            }
            
            this.$('.leave-type-info').html(infoHtml);
        },

        /**
         * Validate form before submission
         */
        _onFormSubmit: function(ev) {
            var validation = PortalUtils.validateForm('.leave-request-form form');
            
            if (!validation.isValid) {
                ev.preventDefault();
                var errorMessage = 'Please fix the following errors:<br/>' + validation.errors.join('<br/>');
                PortalUtils.showNotification(errorMessage, 'error');
                return false;
            }
            
            // Additional custom validation for leave requests
            var fromDate = this.$('input[name="date_from"]').val();
            var toDate = this.$('input[name="date_to"]').val();
            var leaveTypeId = this.$('select[name="holiday_status_id"]').val();
            
            if (!leaveTypeId) {
                ev.preventDefault();
                PortalUtils.showNotification('Please select a leave type.', 'error');
                return false;
            }
            
            if (fromDate && toDate) {
                var days = PortalUtils.calculateDays(fromDate, toDate);
                if (days <= 0) {
                    ev.preventDefault();
                    PortalUtils.showNotification('Invalid date range selected.', 'error');
                    return false;
                }
            }
            
            // Show loading spinner
            PortalUtils.showLoading('.leave-request-form');
            return true;
        },
    });

    // Additional enhancements for leave management
    $(document).ready(function() {
        // Confirm leave cancellation
        $('.btn-cancel-leave').on('click', function(e) {
            e.preventDefault();
            var self = this;
            PortalUtils.confirmAction('Are you sure you want to cancel this leave request?', function() {
                $(self).closest('form').submit();
            });
        });

        // Enhanced filtering for leave history
        $('.leave-filter').on('change', function() {
            var form = $(this).closest('form');
            if (!form.length) {
                // Create a form and submit for filtering
                var url = new URL(window.location.href);
                url.searchParams.set($(this).attr('name'), $(this).val());
                window.location.href = url.toString();
            }
        });

        // Show/hide additional options based on leave type
        $('select[name="holiday_status_id"]').on('change', function() {
            var selectedOption = $(this).find('option:selected');
            var requestUnit = selectedOption.data('request-unit');
            
            if (requestUnit === 'hour') {
                $('.hour-fields').show();
                $('.day-fields').hide();
            } else {
                $('.hour-fields').hide();
                $('.day-fields').show();
            }
        });
    });

});
