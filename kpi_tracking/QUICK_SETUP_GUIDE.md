# KPI Tracking - Quick Setup Card

## 🚀 **5-Minute Setup Guide**

### **Step 1: Install** (1 minute)
- Apps > Search "KPI Tracking" > Install

### **Step 2: User Setup** (2 minutes)
- Settings > Users > Assign groups:
  - **KPI Admin**: Full control
  - **KPI Manager**: Department head
  - **KPI User**: Regular employee

### **Step 3: Create Group** (1 minute)
- KPI Tracking > KPI Groups > Create
- Name: "Sales Team"
- Department: Sales
- Assign users

### **Step 4: Create KPI** (1 minute)
- KPI Tracking > KPI Reports > Create
- Name: "Monthly Revenue"
- Type: Manual
- Target: 100000
- Group: Sales Team

### **Step 5: Submit Value** (30 seconds)
- Click KPI name > Enter value > Submit

---

## 📊 **Common KPI Examples**

### **Sales Department**
```
Monthly Revenue: Target ₹500,000
Lead Conversion: Target 25%
Customer Satisfaction: Target 90%
```

### **HR Department**
```
Training Completion: Target 85%
Employee Retention: Target 95%
Recruitment Time: Target 30 days
```

### **Operations**
```
Process Efficiency: Target 95%
Cost Reduction: Target ₹50,000
Quality Score: Target 98%
```

---

## 🔧 **Auto KPI Formula Examples**

### **Sales Orders Count**
```python
Source Model: sale.order
Filter Field: date_order
Filter Type: this_month
Domain: [('state', '=', 'sale')]
Formula: count_a
```

### **Revenue Calculation**
```python
Source Model: sale.order
Filter Field: date_order
Filter Type: this_month
Domain: [('state', '=', 'sale')]
Formula: sum(record.amount_total for record in records)
```

### **Conversion Rate**
```python
Source Model: crm.lead
Filter Field: create_date
Filter Type: this_month
Domain: [('stage_id.is_won', '=', True)]
Formula: (count_b / count_a) * 100 if count_a > 0 else 0
```

---

## 🎯 **Best Practices**

### **DO's**
✅ Start with 3-5 key KPIs
✅ Set realistic targets
✅ Train users properly
✅ Monitor regularly
✅ Link to action plans

### **DON'Ts**
❌ Create too many KPIs
❌ Set unrealistic targets
❌ Ignore user feedback
❌ Skip regular reviews
❌ Forget to celebrate success

---

## 📞 **Quick Help**

### **Navigation**
- **KPI Groups**: Manage departments
- **KPI Reports**: Create/edit KPIs
- **KPI Submissions**: Submit values
- **My KPIs**: Personal dashboard

### **Support**
- **Email**: info@oneto7solutions.in
- **Website**: https://www.oneto7solutions.in
- **Documentation**: README.md + USER_MANUAL.md
- **Response**: 24-48 hours

---

**Print this card for quick reference!**
**Version**: 18.1.0 | **OneTo7 Solutions**
