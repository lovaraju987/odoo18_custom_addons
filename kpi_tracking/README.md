# KPI Tracking (v10)

## 🔍 Purpose

The **KPI Tracking** module allows Odoo users to define, monitor, and evaluate Key Performance Indicators (KPIs) across different departments. It supports automatic calculations, target scoring, historical submissions, and user-based access control.

---

## ✨ Key Features

- 🧩 Department-Based KPIs (Sales, HR, Operations, etc.)
- ✍️ Manual or Auto-Calculated KPI Inputs
- 🧠 Dynamic Formula Logic (e.g., `(count_a / count_b) * 100`)
- 📁 Report Groups to logically organize KPIs
- 👥 Assign KPIs to Users and Groups
- 📝 Automatic Submission Logging
- 🎯 Target Achievement Tracking with Percentage Score
- 🎨 Color-coded Performance (Green, Yellow, Red)
- 🔔 Email Reminders (Scheduled + Manual Send Button)
- 🔒 Access Roles: Admin, Manager, and User
- 📈 Dashboard-ready (Pivot and Graph support)

---

## 🛠 Models

- `kpi.report`: Defines individual KPIs
- `kpi.report.group`: Groups KPIs for structured reporting
- `kpi.report.submission`: Logs submitted KPI values

---

## 📧 Email Reminder System

- CRON job: Sends reminders daily to users with pending manual KPIs
- Manual button on `kpi.report.group` to trigger reminders on demand
- Email template: `kpi_manual_entry_email_template`

---

## 🔐 Security Groups

| Group        | Permissions                       |
|--------------|------------------------------------|
| KPI Admin    | Full control of all KPIs and groups |
| KPI Manager  | Access to department or group KPIs |
| KPI User     | Access to assigned KPIs only       |

---

## ⚙️ Technical Requirements

- Odoo 17+
- Dependencies: `base`, `hr`, `web`, `board`

---

## 📂 Installation

Place the module in your custom addons directory and install it from the Apps menu.

---

## 📌 Notes

- Be sure to assign users to the correct KPI group (User/Manager/Admin)
- Customize your formula logic using dummy fields `count_a`, `count_b`, etc.
- Validate `source_domain` and `formula_field` are safe and correct before saving

---

## 🧑‍💻 Author

Custom Module by [Your Company Name]

---

## 🔄 Working Flow

### 1. Setup Phase

- Create a **Report Group** (e.g. "Weekly Sales KPIs")
- Under that group, define one or more **KPI records**
- Set KPI Type:
  - `manual`: user must enter value
  - `auto`: value is calculated from a model + domain + optional formula
- For auto KPIs:
  - Define `source_model`, `source_domain`
  - (Optionally) define formula using `count_a`, `count_b`, etc.
- Define `target_type` and `target_value` for scoring

---

### 2. Daily/Weekly Tracking

- **Manual KPI** users input value manually via form view
- **Auto KPI** values get updated automatically via:
  - CRON job (`scheduled_update_kpis`)
  - or manual "Refresh KPI" button

---

### 3. Submission History

- Each KPI update creates a record in `kpi.report.submission`
- Tracks:
  - value
  - target value
  - user who submitted
  - timestamp
- Visible:
  - In KPI form → Submissions tab
  - In Report Group form
  - From dedicated "Submissions" menu

---

### 4. Dashboard Review

- Use Graph and Pivot views to analyze KPIs
- Filter by Department, Report Group, User, etc.

---

### 5. Notifications

- Users receive email reminders for manual KPIs:
  - Automatically via CRON
  - Manually from Report Group form via "Send Reminder" button




  suggestions features:


  Perfect! Since you want to build and scale your own kpi_tracking module, here’s a roadmap of powerful initiatives and improvements you can implement natively, without depending on third-party apps.

⸻

🚀 Suggested Initiatives to Evolve Your KPI Module

⸻

✅ 1. Performance Alerts & Notifications

Feature	Description
🔔 Color-based alerts	Show progress bars with red/yellow/green based on achievement_percent
📧 Email if under target	CRON sends warning emails to users whose KPIs dropped below target
✅ Chatter message log	Post automated messages when KPIs are updated or off track



⸻

✅ 2. KPI Scheduling & Deadline Enforcement

Feature	Description
🕒 Deadline Field	Each KPI can define a submission deadline (weekly, monthly, etc.)
⏰ Missed Submission Tracker	Mark missed submissions; show badge count on user dashboard
🗓 Calendar View	Show KPI due dates visually using Odoo calendar



⸻

✅ 3. Employee Performance Dashboard

Feature	Description
📊 KPI Summary Card	Show number of KPIs, achievement %, and pending ones for a user
📅 Weekly KPI Widget	What’s due this week for me?
💬 Manager Insights	Rank team members based on compliance or target achievement



⸻

✅ 4. Weighted KPIs and Scores

Feature	Description
🧮 KPI Weight Field	Assign weight (importance) to each KPI
📊 Scorecard Calculation	Calculate final score = ∑ (achievement × weight)
🏆 Top Performers	List top 3 employees or teams based on score



⸻

✅ 5. KPI Templates & Duplication

Feature	Description
📋 Save as Template	Convert any KPI group to a reusable template
🌀 Generate Weekly Copy	Auto-create KPI instances each week from templates
👥 Assign Template by Role	Auto-assign standard KPIs when a new user is added to a department



⸻

✅ 6. Feedback & Annotation System

Feature	Description
🗨 Manager Comments	Let managers give feedback on submitted KPIs
🟢 KPI Justification Field	Allow employees to comment when below/above target
🔍 Audit Trail View	Who updated what and when (already supported via kpi.report.submission)



⸻

✅ 7. Reporting & Export Tools

Feature	Description
📤 Export to Excel	Add button to export current KPI dashboard or group to .xlsx
🧾 Download Weekly Report	Button to generate a report summary (PDF or XLSX)
📅 Generate PDF by Week	Summary for each week by department with targets, results, %s



⸻

🧩 Build Only What You Need, One Piece at a Time

This roadmap lets you:
	•	Avoid feature bloat
	•	Stay aligned with your team workflow
	•	Keep full control of customizations


road map:


Awesome — here’s a clean, version-wise roadmap to help you build your kpi_tracking module into a complete, scalable, team-wide performance system:

⸻

🧭 KPI Tracking Module Enhancement Roadmap

⸻

✅ v1.0 — Core KPI Management (✅ Already Completed)
	•	Manual & Auto KPI Types
	•	KPI Grouping
	•	Target Value & Achievement %
	•	Submission Logging
	•	Daily CRON Update
	•	Role-based Access (User / Manager / Admin)
	•	Email Reminders
	•	Smart Button: Send Manual Reminders
	•	Department & Assignment Filters

⸻

🧩 v1.1 – Visual Insights & Color Alerts (Next Priority)

🎯 Goal: Help users instantly understand performance from dashboard

Feature	Status
✅ Color-coded achievement_percent (red/yellow/green)	
✅ KPI progress bar widget	
🚨 Visual “Below Target” warnings	
📌 Decorated list/tree views with conditional styling	
📊 Achievement summary view per department or user	



⸻

🧪 v1.2 – Deadlines & Compliance Tracking

🎯 Goal: Ensure KPIs are submitted on time

Feature	Status
⏰ Submission Deadline field (e.g. Every Monday)	
🛑 Detect missing manual KPI entries	
🔔 Alert/notify when overdue	
🗓 KPI Calendar view (submission schedule)	
📈 KPI compliance % tracking for each user	



⸻

🧮 v1.3 – Weighted KPI Scoring & Performance Ranks

🎯 Goal: Quantify performance more accurately

Feature	Status
📊 Weight field on KPI (importance %)	
🧮 Score = Achievement × Weight	
🏆 Weekly score summary for each employee	
🥇 Leaderboard: Top 3 performers per team	



⸻

📑 v1.4 – Export & Reporting Tools

🎯 Goal: Let managers download/share performance reports

Feature	Status
📥 Export KPI group to .xlsx	
🧾 Weekly summary report (PDF or Excel)	
📤 Auto-send report to manager (optional)	
📁 KPI data dump for audit (CSV or Excel)	



⸻

🧠 v1.5 – Smart Templates & Auto KPI Creation

🎯 Goal: Make setup easier and reusable

Feature	Status
🧩 Save KPI group as template	
🔄 Auto-generate KPIs weekly from template	
👥 Auto-assign template based on department or role	
🚀 Duplicate existing groups easily	



⸻

💬 v1.6 – Feedback & Review System

🎯 Goal: Add context to performance

Feature	Status
💬 Manager feedback field on submissions	
🟡 Justification notes for below-target KPIs	
🧾 Audit trail view of all updates	
📌 Submission comment threading (basic chatter)	



⸻

🚦 Suggested Rollout Plan

Version	Focus	Timeline Suggestion
v1.1	UI Feedback (Color Alerts)	Immediate
v1.2	Submission Compliance	Week 2
v1.3	Weighted KPI Score	Week 3
v1.4	Reporting Tools (Excel)	Week 4
v1.5	Templates & Auto Copy	Optional or later
v1.6	Feedback System	Bonus phase



⸻

Let me know which one you’d like to begin building first (v1.1 → color alerts, or v1.2 → deadlines)? I’ll guide you with clean code and view changes step-by-step.

