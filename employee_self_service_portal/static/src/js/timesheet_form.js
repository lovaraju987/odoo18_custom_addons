$(document).ready(function() {
    // Handle project selection change for both single and bulk forms
    $('#project_id, #common_project_id').change(function() {
        var projectId = $(this).val();
        var taskSelects;
        
        // Determine which task selects to update based on form type
        if ($(this).attr('id') === 'common_project_id') {
            // Bulk form
            taskSelects = $('.task-select');
        } else {
            // Single form
            taskSelects = $('#task_id');
        }
        
        // Clear task options
        taskSelects.each(function() {
            $(this).empty().append('<option value="">Select a task</option>');
        });
        
        if (projectId) {
            // Load tasks for selected project
            $.ajax({
                url: '/my/employee/timesheets/get_tasks',
                type: 'GET',
                data: {
                    'project_id': projectId
                },
                success: function(response) {
                    if (response.success && response.tasks) {
                        taskSelects.each(function() {
                            var taskSelect = $(this);
                            $.each(response.tasks, function(index, task) {
                                taskSelect.append('<option value="' + task.id + '">' + task.name + '</option>');
                            });
                            
                            // Add option to create new task
                            taskSelect.append('<option value="new_task" style="font-weight: bold; color: #007bff;">+ Create New Task</option>');
                        });
                    } else {
                        console.log('No tasks found or error:', response.error);
                        taskSelects.each(function() {
                            $(this).append('<option value="new_task" style="font-weight: bold; color: #007bff;">+ Create New Task</option>');
                        });
                    }
                },
                error: function() {
                    console.log('Error loading tasks');
                    taskSelects.each(function() {
                        $(this).append('<option value="new_task" style="font-weight: bold; color: #007bff;">+ Create New Task</option>');
                    });
                }
            });
        }
    });
    
    // Handle task selection change for both single and bulk forms (for new task creation)
    $(document).on('change', '#task_id, .task-select', function() {
        var taskId = $(this).val();
        var currentSelect = $(this);
        
        if (taskId === 'new_task') {
            showNewTaskModal(currentSelect);
        }
    });
    
    // Function to show new task creation modal
    function showNewTaskModal(taskSelect) {
        var projectId = $('#project_id').val() || $('#common_project_id').val();
        
        if (!projectId) {
            alert('Please select a project first');
            taskSelect.val('');
            return;
        }
        
        var taskName = prompt('Enter the name for the new task:');
        
        if (taskName && taskName.trim()) {
            // Create new task via AJAX
            $.ajax({
                url: '/my/employee/timesheets/create_task',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    'jsonrpc': '2.0',
                    'method': 'call',
                    'params': {
                        'project_id': projectId,
                        'task_name': taskName.trim()
                    }
                }),
                success: function(response) {
                    if (response.result && response.result.success && response.result.task_id) {
                        // Add the new task to all task dropdowns and select it in the current one
                        var newOption = '<option value="' + response.result.task_id + '">' + response.result.task_name + '</option>';
                        
                        // Update all task selects
                        $('#task_id, .task-select').each(function() {
                            $(this).find('option[value="new_task"]').before(newOption);
                        });
                        
                        // Select the new task in the current dropdown
                        taskSelect.val(response.result.task_id);
                        
                        alert('Task "' + response.result.task_name + '" created successfully!');
                    } else {
                        alert('Error creating task: ' + (response.result.error || 'Unknown error'));
                        taskSelect.val('');
                    }
                },
                error: function() {
                    alert('Error creating task. Please try again.');
                    taskSelect.val('');
                }
            });
        } else {
            taskSelect.val('');
        }
    }
    
    // Handle form submission validation
    $('#timesheet-form').submit(function(e) {
        var projectId = $('#project_id').val();
        var taskId = $('#task_id').val();
        var date = $('#date').val();
        var unitAmount = parseFloat($('#unit_amount').val());
        var name = $('#name').val().trim();
        
        var errors = [];
        
        if (!projectId) {
            errors.push('Please select a project');
        }
        
        if (!taskId || taskId === 'new_task') {
            errors.push('Please select a task');
        }
        
        if (!date) {
            errors.push('Please select a date');
        }
        
        if (!unitAmount || unitAmount <= 0) {
            errors.push('Please enter valid hours (greater than 0)');
        }
        
        if (!name) {
            errors.push('Please enter a description');
        }
        
        if (errors.length > 0) {
            e.preventDefault();
            alert('Please fix the following errors:\n\n' + errors.join('\n'));
            return false;
        }
        
        // Check for future dates
        var selectedDate = new Date(date);
        var today = new Date();
        today.setHours(0, 0, 0, 0);
        
        if (selectedDate > today) {
            if (!confirm('You are entering timesheet for a future date. Are you sure you want to continue?')) {
                e.preventDefault();
                return false;
            }
        }
        
        return true;
    });
    
    // Auto-save functionality for edit forms
    if ($('#timesheet-edit-form').length > 0) {
        var originalValues = {};
        
        // Store original values
        $('#timesheet-edit-form input, #timesheet-edit-form select, #timesheet-edit-form textarea').each(function() {
            originalValues[this.name] = $(this).val();
        });
        
        // Check for changes before leaving page
        $(window).on('beforeunload', function(e) {
            var hasChanges = false;
            
            $('#timesheet-edit-form input, #timesheet-edit-form select, #timesheet-edit-form textarea').each(function() {
                if (originalValues[this.name] !== $(this).val()) {
                    hasChanges = true;
                    return false;
                }
            });
            
            if (hasChanges) {
                return 'You have unsaved changes. Are you sure you want to leave?';
            }
        });
        
        // Remove beforeunload when form is submitted
        $('#timesheet-edit-form').submit(function() {
            $(window).off('beforeunload');
        });
    }
    
    // Confirmation for delete actions
    $('.btn-delete-timesheet').click(function(e) {
        if (!confirm('Are you sure you want to delete this timesheet entry? This action cannot be undone.')) {
            e.preventDefault();
            return false;
        }
    });
    
    // Hours input formatting
    $('#unit_amount').on('input', function() {
        var value = $(this).val();
        
        // Allow only numbers and decimal point
        var cleaned = value.replace(/[^0-9.]/g, '');
        
        // Ensure only one decimal point
        var parts = cleaned.split('.');
        if (parts.length > 2) {
            cleaned = parts[0] + '.' + parts.slice(1).join('');
        }
        
        // Limit decimal places to 2
        if (parts[1] && parts[1].length > 2) {
            cleaned = parts[0] + '.' + parts[1].substring(0, 2);
        }
        
        $(this).val(cleaned);
    });
    
    // Date input validation
    $('#date').change(function() {
        var selectedDate = new Date($(this).val());
        var today = new Date();
        var maxPastDate = new Date();
        maxPastDate.setMonth(today.getMonth() - 3); // 3 months ago
        
        if (selectedDate < maxPastDate) {
            alert('Warning: You are entering timesheet for a date more than 3 months ago. Please verify the date is correct.');
        }
    });
    
    // Bulk timesheet functionality
    var taskEntryIndex = 1;
    
    // Add new task entry
    $('#add-task-entry').click(function() {
        var newEntry = $('.task-entry').first().clone();
        newEntry.attr('data-index', taskEntryIndex);
        newEntry.find('input, select').val('');
        newEntry.find('.remove-task').show();
        
        // Update the task select with current options if project is selected
        var projectId = $('#common_project_id').val();
        if (projectId) {
            // Trigger change event to load tasks for this new select
            setTimeout(function() {
                $('#common_project_id').trigger('change');
            }, 100);
        }
        
        $('#task-entries').append(newEntry);
        taskEntryIndex++;
        
        updateRemoveButtons();
    });
    
    // Remove task entry
    $(document).on('click', '.remove-task', function() {
        $(this).closest('.task-entry').remove();
        updateRemoveButtons();
    });
    
    function updateRemoveButtons() {
        var entries = $('.task-entry');
        if (entries.length <= 1) {
            $('.remove-task').hide();
        } else {
            $('.remove-task').show();
        }
    }
    
    // Bulk form validation
    $('#bulk-timesheet-form').submit(function(e) {
        var projectId = $('#common_project_id').val();
        var date = $('#common_date').val();
        var errors = [];
        
        if (!projectId) {
            errors.push('Please select a project');
        }
        
        if (!date) {
            errors.push('Please select a date');
        }
        
        // Validate each task entry
        $('.task-entry').each(function(index) {
            var taskId = $(this).find('.task-select').val();
            var hours = $(this).find('input[name="hours[]"]').val();
            var description = $(this).find('input[name="descriptions[]"]').val();
            
            var entryNum = index + 1;
            
            if (!taskId || taskId === 'new_task') {
                errors.push('Please select a task for entry ' + entryNum);
            }
            
            if (!hours || parseFloat(hours) <= 0) {
                errors.push('Please enter valid hours for entry ' + entryNum);
            }
            
            if (!description || !description.trim()) {
                errors.push('Please enter a description for entry ' + entryNum);
            }
        });
        
        if (errors.length > 0) {
            e.preventDefault();
            alert('Please fix the following errors:\n\n' + errors.join('\n'));
            return false;
        }
        
        return true;
    });
});
