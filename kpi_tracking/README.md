# KPI Tracking Module

## 🔍 Overview

The **KPI Tracking** module is a comprehensive performance management system for Odoo 18 that enables organizations to define, monitor, and evaluate Key Performance Indicators (KPIs) across different departments. It supports both manual data entry and automatic calculations with sophisticated formula evaluation.

---

## ✨ Key Features

### 📊 **KPI Management**
- **Manual KPIs**: User-entered values with validation and approval workflows
- **Automatic KPIs**: Formula-based calculations from any Odoo model
- **Target Types**: Number, Percentage, Currency (₹), Boolean (Achieved/Not Achieved), Duration (Hours)
- **Performance Direction**: Higher-is-better or Lower-is-better scoring logic

### 🏢 **Department Organization**
- Department-wise KPI organization (Sales, HR, Operations, Marketing, Finance, etc.)
- Report Groups for logical KPI clustering
- User and employee assignments with role-based access

### 🎯 **Performance Tracking**
- Target vs Achievement percentage calculation
- Color-coded performance indicators (Excellent, Good, Average, Needs Improvement, Underperformance)
- Historical submission tracking and audit trails
- Progress bars and visual performance indicators

### 🔔 **Automation & Notifications**
- Scheduled automatic KPI updates via CRON jobs
- Email reminders for manual KPI submissions
- Batch processing for large datasets
- Automated group-level performance aggregation

### 🔒 **Security & Access Control**
- Three-tier security model: Admin, Manager, User
- Record-level access rules
- Formula security validation
- Input sanitization and validation

---

## 🛠 Data Models

| Model | Description |
|-------|-------------|
| `kpi.report` | Main KPI definition with calculation logic |
| `kpi.report.group` | KPI grouping and department organization |
| `kpi.report.submission` | Individual KPI submission history |
| `kpi.report.group.submission` | Group-level performance history |

---

## 🔐 Security Groups

| Group | Permissions | Access Level |
|-------|-------------|--------------|
| **KPI Admin** | Full control of all KPIs, groups, and submissions | Create, Read, Write, Delete |
| **KPI Manager** | Department/group KPIs management | Create, Read, Write |
| **KPI User** | Assigned KPIs only | Read, Submit values |

---

## ⚙️ Configuration

### **Manual KPI Setup**
1. Create a Report Group for your department
2. Define KPI with type 'Manual'
3. Set target type and target value
4. Assign users who will submit values
5. Configure email reminders if needed

### **Automatic KPI Setup**
1. Create KPI with type 'Auto'
2. Select source model (e.g., sale.order, crm.lead)
3. **Select filter field** from dropdown (all fields are now available)
4. Set filter type (today, this week, this month)
5. **Build domain filter** using the visual domain builder (no Python code required)
6. Create formula using available variables:
   - `count_a`: Total records in base domain
   - `count_b`: Records matching filtered domain
   - `records`: Actual record objects
   - `assigned_user`: Current assigned user
   - `today`: Current date

### **Formula Examples**
```python
# Percentage calculation
(count_b / count_a) * 100

# Sum of amounts
sum(record.amount_total for record in records)

# Average calculation
sum(record.amount_total for record in records) / len(records) if records else 0

# Conditional logic
sum(record.amount_total for record in records if record.state == 'sale')
```

---

## 📱 User Interface

### **Dashboard Views**
- **List View**: Quick overview with progress bars and color coding
- **Form View**: Detailed KPI configuration and submission
- **Graph View**: Visual performance trends
- **Pivot View**: Multi-dimensional analysis

### **Key UI Elements**
- Progress bars for achievement visualization
- Color-coded badges for performance levels
- **Visual Domain Builder**: Intuitive interface for creating record filters without Python code
- **Enhanced Filter Field Selection**: All model fields available in dropdown (not just date/datetime)
- Contextual help text for complex fields
- Submission history tracking
- Test buttons for domain and formula validation

---

## 🚀 Installation & Setup

### **Prerequisites**
- Odoo 18.0 or later
- Dependencies: `base`, `hr`, `web`

### **Installation Steps**
1. Copy the module to your Odoo addons directory
2. Update the app list
3. Install the "KPI Tracking" module
4. Configure security groups and assign users
5. Create your first KPI Report Group
6. Define KPIs and start tracking!

---

## 🎨 Domain Builder Feature

The KPI Tracking module now includes a **Visual Domain Builder** that makes it easy to create record filters without writing Python code.

### **How to Use the Domain Builder**

1. **Open a KPI**: Go to KPI Reports → Open any KPI with 'Auto' type
2. **Navigate to Auto Tracking Configuration**: Scroll to the "Auto Tracking Configuration" section
3. **Select Source Model**: Choose the Odoo model you want to filter (e.g., sale.order, hr.employee)
4. **Click on Source Domain**: The domain builder widget will open in a popup dialog
5. **Build Your Filter Visually**:
   - Click "Add node" to add filter conditions
   - Select fields from dropdown menus
   - Choose operators (=, !=, <, >, contains, etc.)
   - Enter values for comparison
   - Use AND/OR logic to combine conditions
6. **Save the Domain**: Click "Save" to apply your domain filter

### **Domain Builder Benefits**

- **No Python Knowledge Required**: Build complex filters using a visual interface
- **Real-time Field Discovery**: All fields from the selected model are available in dropdowns
- **Operator Suggestions**: Appropriate operators are suggested based on field types
- **Syntax Validation**: Built-in validation ensures your domain is correctly formatted
- **Visual Logic**: See AND/OR groupings clearly in the interface

### **Example Domain Filters**

**Sales Orders from Last Month:**
```
[('date_order', '>=', '2024-01-01'), ('date_order', '<=', '2024-01-31')]
```

**Confirmed Sales Orders with Specific Salesperson:**
```
[('state', 'in', ['sale', 'done']), ('user_id.name', '=', 'John Doe')]
```

**HR Employees in Specific Department:**
```
[('department_id.name', 'ilike', 'sales'), ('active', '=', True)]
```

---

## 📧 Email System

The module includes an automated email reminder system:

- **Template**: `kpi_manual_entry_email_template`
- **Frequency**: Daily CRON job for manual KPI reminders
- **Manual Trigger**: Button on Report Groups to send immediate reminders
- **Recipients**: Assigned users with pending manual submissions

---

## 🔄 Automation

### **CRON Jobs**
1. **Auto Refresh KPIs**: Daily update of automatic KPIs
2. **Manual KPI Reminders**: Daily email reminders for pending submissions

### **Batch Processing**
- Efficient processing of large KPI datasets
- Memory-optimized calculations
- Error handling and logging

---

## 🛡️ Security Features

- **Formula Security**: Validation against dangerous code execution
- **Input Sanitization**: Comprehensive data validation
- **Access Control**: Record-level security rules
- **Audit Trail**: Complete submission history tracking

---

## 🎯 Best Practices

### **KPI Design**
- Use clear, measurable KPI names
- Set realistic and achievable targets
- Assign appropriate users to KPIs
- Regularly review and update targets

### **Formula Safety**
- Test formulas thoroughly before deployment
- Use the domain test button to validate filters
- Avoid complex calculations in formulas
- Document formula logic for maintenance

### **Performance Optimization**
- Use specific domains to limit record searches
- Avoid overly complex formulas
- Regular cleanup of old submissions
- Monitor CRON job performance

---

## 📋 Troubleshooting

### **Common Issues**
- **Formula Errors**: Use the Test Domain button to validate syntax
- **Permission Issues**: Check user group assignments
- **Performance Problems**: Review domain filters and optimize queries
- **Email Issues**: Verify email template configuration

### **Support**
For technical support and customization requests, please contact your system administrator or Odoo partner.

---

## 🚀 Future Enhancements Roadmap

### **v1.1 - Visual Insights & Alerts**
- Enhanced color-coded performance indicators
- Real-time dashboard updates
- Performance threshold alerts

### **v1.2 - Deadlines & Compliance**
- KPI submission deadlines
- Compliance tracking and reporting
- Calendar view for KPI schedules

### **v1.3 - Advanced Analytics**
- Weighted KPI scoring
- Performance rankings and leaderboards
- Trend analysis and predictions

### **v1.4 - Reporting & Export**
- Excel export functionality
- PDF report generation
- Automated report distribution

### **v1.5 - Templates & Automation**
- KPI templates for quick setup
- Auto-generation of recurring KPIs
- Department-based auto-assignment

---

## 📈 Version History

- **v18.1.0**: Odoo 18 compatibility, enhanced security, improved UI
- Enhanced code quality and performance optimizations
- Added comprehensive validation and error handling
- Improved user experience with contextual help

---

## 📄 License

This module is licensed under LGPL-3.

---

## 🏪 Odoo App Store Preparation

This module is prepared for publication on the Odoo App Store with the following commercial settings:

### 💰 **Commercial Information**
- **Price**: $20 USD
- **License**: OPL-1 (Odoo Proprietary License)
- **Category**: Human Resources
- **Author**: OneTo7 Solutions
- **Support**: info@oneto7solutions.in
- **Website**: https://www.oneto7solutions.in

### 📦 **Package Contents**
- ✅ Demo data with sample KPIs and submissions
- ✅ Professional README documentation
- ✅ Commercial license (OPL-1)
- ✅ Security and access control rules
- ✅ Email templates and CRON jobs
- ⚠️ **TODO**: Add static images (banner, icon, screenshots)

### 🖼️ **Required Images** (to be added)
Place these images in `static/description/`:
- `banner.png` (1200x300px) - App Store banner
- `icon.png` (128x128px) - Module icon
- `kpi_dashboard.png` (800x600px) - Dashboard screenshot
- `kpi_form.png` (800x600px) - Form view screenshot
- `kpi_reports.png` (800x600px) - Reports screenshot

### 🔍 **Pre-Publication Checklist**
- [x] Code quality review and refactoring
- [x] Security validation and access controls
- [x] Documentation cleanup and enhancement
- [x] Demo data creation
- [x] Commercial license and pricing
- [x] Manifest file optimization
- [ ] Static images creation
- [ ] Final testing in clean Odoo 18 instance
- [ ] App Store submission and review

---

## 📋 **Step-by-Step User Guide**

### 🚀 **Getting Started - Your First KPI**

#### **Step 1: Install and Setup**
1. Install the KPI Tracking module from Apps
2. Go to **Settings > Users & Companies > Users**
3. Add users to appropriate KPI groups:
   - **KPI Admin**: Full control (IT/Management)
   - **KPI Manager**: Department management (Team Leaders)
   - **KPI User**: Submit KPI values (Employees)

#### **Step 2: Create Your First KPI Group**
1. Navigate to **KPI Tracking > KPI Groups**
2. Click **Create** and fill in:
   - **Name**: "Sales Team Performance"
   - **Department**: Sales
   - **Description**: "Track monthly sales targets and achievements"
   - **Frequency**: Monthly
   - **Start/End Dates**: Set your reporting period
   - **Assigned Users**: Select team members

#### **Step 3: Create a Manual KPI**
1. Go to **KPI Tracking > KPI Reports**
2. Click **Create** and configure:
   - **KPI Name**: "Monthly Sales Revenue"
   - **KPI Group**: Select "Sales Team Performance"
   - **Target Type**: Currency
   - **Target Value**: 100000 (₹1,00,000)
   - **Calculation Type**: Manual
   - **Performance Direction**: Higher is Better
   - **Assigned User**: Select responsible person

#### **Step 4: Submit KPI Values**
1. Users can submit values from:
   - **KPI Reports list**: Click on KPI name
   - **My KPIs**: Shows only assigned KPIs
   - **KPI Submissions**: Historical view
2. Enter **Actual Value** and optional **Notes**
3. Click **Submit** to save

---

## 🔧 **Advanced KPI Configuration**

### **Creating Automatic KPIs**

#### **Sales Order Count Example**
```python
# KPI: Monthly Sales Order Count
Name: "Sales Orders This Month"
Calculation Type: Auto
Source Model: sale.order
Filter Field: date_order (selected from dropdown - all fields available)
Filter Type: this_month
Domain Filter: [('state', '=', 'sale')] (built using visual domain builder)
Formula: count_a
Target: 50
```

#### **Revenue Calculation Example**
```python
# KPI: Monthly Revenue
Name: "Monthly Revenue"
Calculation Type: Auto
Source Model: sale.order
Filter Field: date_order (selected from dropdown - all fields available)
Filter Type: this_month
Domain Filter: [('state', '=', 'sale')] (built using visual domain builder)
Formula: sum(record.amount_total for record in records)
Target: 500000
```

#### **Conversion Rate Example**
```python
# KPI: Lead to Sale Conversion Rate
Name: "Lead Conversion Rate"
Calculation Type: Auto
Source Model: crm.lead
Filter Field: create_date (selected from dropdown - all fields available)
Filter Type: this_month
Domain Filter: [('stage_id.is_won', '=', True)] (built using visual domain builder)
Formula: (count_b / count_a) * 100 if count_a > 0 else 0
Target: 25
```

### **Formula Variables Reference**
- **`count_a`**: Total records matching base domain
- **`count_b`**: Records matching filtered domain
- **`records`**: Actual record objects for calculations
- **`assigned_user`**: Current user context
- **`today`**: Current date

---

## 📊 **KPI Monitoring & Analytics**

### **Dashboard Views**

#### **List View Features**
- **Progress Bars**: Visual achievement percentage
- **Color Coding**: 
  - 🟢 Green: >90% achievement
  - 🟡 Yellow: 70-90% achievement
  - 🔴 Red: <70% achievement
- **Quick Actions**: Submit, Edit, View History

#### **Form View Details**
- **Performance Metrics**: Target vs Actual
- **Submission History**: Track all submissions
- **Performance Graph**: Trend analysis
- **Test Buttons**: Validate formulas and domains

#### **Graph View**
- **Line Charts**: Performance trends over time
- **Bar Charts**: Compare multiple KPIs
- **Pivot Tables**: Multi-dimensional analysis

### **Performance Monitoring**

#### **Individual KPI Tracking**
1. **Current Status**: Real-time achievement percentage
2. **Historical Trends**: Performance over time
3. **Submission Frequency**: Track regularity
4. **Performance Alerts**: Email notifications for targets

#### **Department-Level Monitoring**
1. **Group Performance**: Overall department achievement
2. **Team Comparisons**: Inter-departmental analysis
3. **Resource Allocation**: Identify improvement areas
4. **Trend Analysis**: Long-term performance patterns

---

## 📧 **Email Notifications & Reminders**

### **Automated Reminders**
- **Daily CRON Job**: Checks for pending manual KPIs
- **Email Template**: Professional reminder format
- **Recipient Logic**: Only assigned users with pending submissions
- **Customizable**: Modify email content and frequency

### **Manual Reminders**
- **Group Level**: Send reminders to all group members
- **Individual Level**: Target specific users
- **Immediate Send**: Button-triggered notifications
- **Bulk Operations**: Multiple KPIs at once

---

## 🎯 **Best Practices for KPI Success**

### **KPI Design Principles**
1. **SMART Goals**: Specific, Measurable, Achievable, Relevant, Time-bound
2. **Clear Naming**: Use descriptive, unambiguous names
3. **Realistic Targets**: Set achievable yet challenging goals
4. **Regular Review**: Update targets based on performance
5. **User Training**: Ensure all users understand the process

### **Department-Specific Examples**

#### **Sales Department**
- Monthly Revenue Achievement
- Lead Conversion Rate
- Customer Acquisition Cost
- Sales Cycle Time
- Customer Satisfaction Score

#### **HR Department**
- Employee Retention Rate
- Training Completion Rate
- Recruitment Time
- Employee Satisfaction
- Performance Review Completion

#### **Operations Department**
- Process Efficiency Rate
- Cost Reduction Achieved
- Quality Score
- Delivery Time
- Resource Utilization

#### **Marketing Department**
- Campaign ROI
- Lead Generation Rate
- Website Traffic Growth
- Social Media Engagement
- Brand Awareness Score

### **Common Pitfalls to Avoid**
1. **Too Many KPIs**: Focus on 3-5 key metrics per department
2. **Unrealistic Targets**: Set achievable goals
3. **Infrequent Updates**: Regular monitoring is essential
4. **No Action Plans**: Link KPIs to improvement initiatives
5. **Lack of Training**: Ensure users understand the system

---

## 🔍 **Troubleshooting Guide**

### **Common Issues**

#### **Formula Errors**
**Problem**: "Invalid formula syntax"
**Solution**: 
1. Use the **Test Domain** button to validate
2. Check variable names (count_a, count_b, records)
3. Ensure proper Python syntax
4. Test with simple formulas first

#### **Permission Issues**
**Problem**: "Access denied to KPI records"
**Solution**:
1. Check user group assignments
2. Verify record-level security rules
3. Ensure proper role assignments
4. Contact system administrator

#### **Email Not Sending**
**Problem**: "KPI reminders not received"
**Solution**:
1. Check email server configuration
2. Verify email template exists
3. Ensure CRON job is active
4. Check user email addresses

#### **Performance Issues**
**Problem**: "Slow KPI calculations"
**Solution**:
1. Optimize domain filters
2. Reduce formula complexity
3. Use specific date ranges
4. Consider database indexing

### **Getting Help**
- **Documentation**: Comprehensive README included
- **Support Email**: info@oneto7solutions.in
- **Website**: https://www.oneto7solutions.in
- **Community**: Odoo forums and community support

---

## 📚 **Quick Reference Card**

### **Navigation Menu**
- **KPI Tracking > KPI Groups**: Manage departments
- **KPI Tracking > KPI Reports**: Create and configure KPIs
- **KPI Tracking > KPI Submissions**: Submit and view values
- **KPI Tracking > My KPIs**: Personal KPI dashboard

### **Key Actions**
- **Create KPI**: Reports > Create
- **Submit Value**: Click KPI name > Submit
- **Send Reminder**: Group form > Send Email
- **Test Formula**: KPI form > Test Domain
- **View History**: Submissions tab in KPI form

### **User Roles**
- **Admin**: Full system access
- **Manager**: Department KPIs only
- **User**: Assigned KPIs only

### **Support Shortcuts**
- **F1**: Help documentation
- **Ctrl+K**: Quick search
- **Alt+M**: Main menu
- **Ctrl+S**: Save current record