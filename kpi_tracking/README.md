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
3. Define filter field for date filtering
4. Set filter type (today, this week, this month)
5. Write domain filter for record selection
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