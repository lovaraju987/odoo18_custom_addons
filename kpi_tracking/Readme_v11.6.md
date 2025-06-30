Here’s the draft module documentation based on the extracted kpi_tracking_v11.6 module:

⸻

📦 Module: KPI Tracking

Version: 11.6
Author: OneTo7 Custom Team
Last Updated: 2025-04-22

⸻

🎯 Purpose

To track, calculate, and analyze department-wise performance indicators (KPIs) using both manual and automated logic integrated with Odoo models, filters, and user-based access controls.

⸻

✅ Key Features

Feature	Description
Department-Wise KPI Setup	Configure KPIs per department (Sales, Ops, Marketing, etc.)
Manual & Auto KPI Modes	Enter manual values or compute from models with filters + formulas
KPI Submission Logging	Track daily/weekly KPI submissions per user with audit log
Target Achievement %	Compute achievement percent vs targets with smart logic
Weighted Group Scoring	Group KPIs with customizable priority weights
Role-Based Access Control	Admins manage everything; Managers submit; Users view-only
Custom Report Grouping	Organize KPIs into Weekly/Monthly reports
Visual Dashboard & Graph Views	Includes progress bars, graphs, and pivot analytics
Cron-based Auto Refresh	Scheduled updates for automated KPIs
Email Reminders	Remind users to submit pending manual KPIs



⸻

🔁 Models Introduced

Model	Description
kpi.report	Main KPI model with logic for tracking, targets, filters, formulas
kpi.report.group	Organizes KPIs into logical reporting groups
kpi.report.submission	History of each KPI submission (user/date-wise)



⸻

⚙️ Fields & Logic Highlights
	•	KPI Types: manual, auto
	•	Target Types: number, percent, currency, boolean, duration
	•	Achievement Direction: >=, <= (for inversion logic like wastage)
	•	Source Model / Domain / Formula: Dynamically configured to evaluate KPIs from any model
	•	Group Achievement: Weighted based on priority_weight per KPI
	•	Advanced Filtering: Using filter_field + filter_type + source_domain
	•	Slot-based logic: Slot length tracking, technician efficiency, lead response time, etc.
	•	Inventory Logic: Stock accuracy %, quantity summaries, compliance

⸻

🔐 Access Groups

Group ID	Role Permissions
group_kpi_admin	Full create/edit/delete access
group_kpi_manager	Can submit manual KPIs, view reports
group_kpi_user	Can only view their assigned KPIs and history



⸻

🔒 Record Rules
	•	Users see only their assigned KPIs or groups they’re linked to
	•	Managers see KPIs based on department or groups linked via employee profile
	•	Admins have unrestricted access

⸻

🛠️ Automation & Utilities
	•	Cron: Auto Refresh KPI Reports (runs daily)
	•	Buttons:
	•	Test Domain – to validate dynamic domain logic
	•	Refresh KPI Now – for manual KPI update
	•	Submit Manual KPI – for entering manual values

⸻

📈 UI Elements
	•	Tree: Overview with progress bars
	•	Form: Detailed configuration + submission history
	•	Graph & Pivot views for dashboards
	•	Search filters: department, report, KPI type

⸻

Let me know if you’d like this saved as a PDF or added to the module as a README.md. ￼


Work Flow:

Here is a clear and complete KPI Tracking Module Workflow based on your current version v11.6:

⸻

🔄 KPI Tracking – Workflow Documentation

⸻

🧩 Step 1: Define KPI Groups

Model: kpi.report.group
	•	Created by Admin.
	•	Each group represents a reporting unit (e.g. Weekly Sales Report, Store Manager Monthly Report).
	•	Assigned to specific employees via assigned_employee_ids.
	•	Linked to departments like Sales, Store, Operations, etc.

🛠 Admin Action:
Create → Assign Employees → Select Department

⸻

🧮 Step 2: Create KPIs

Model: kpi.report
	•	Created by Admin.
	•	Linked to a group via report_id.
	•	Assigned to users (salespeople, store managers, etc.).
	•	Define KPI nature:
	•	kpi_type: Manual / Auto
	•	target_type: Number, %, Currency, Boolean, Duration
	•	kpi_direction: >= / <= (impacts achievement % logic)
	•	priority_weight: Used in group achievement %
	•	If auto, configure:
	•	source_model_id: any model (ex: crm.lead, project.task)
	•	filter_field: used with filter_type (today, week, month)
	•	source_domain: advanced dynamic filters (ex: [('stage_id.name', '=', 'Closed')])
	•	formula_field: Python expression (e.g. sum(r.amount for r in records))

🛠 Admin Action:
Configure all KPIs → Auto/manual settings → Target + formula

⸻

📊 Step 3: KPI Value Evaluation

A) Manual KPIs
	•	Managers enter value in manual_value
	•	Click “Submit Manual KPI” → creates a kpi.report.submission record
	•	Calculates:
	•	value
	•	achievement_percent

📌 Editable only for group_kpi_admin and group_kpi_manager

B) Auto KPIs
	•	Automatically computed via:
	•	scheduled_update_kpis() (CRON or manual)
	•	Uses domain, filters, and formula to calculate value
	•	Auto creates kpi.report.submission per assigned user
	•	Stores:
	•	Record counts (count_a, count_b)
	•	Formula result in value
	•	achievement_percent

⸻

📈 Step 4: Group Achievement Calculation

Model: kpi.report.group
	•	Field: group_achievement_percent
	•	Logic:

sum(kpi.achievement_percent * kpi.priority_weight) / sum(kpi.priority_weight)


	•	Real-time recomputation whenever a KPI’s achievement_percent changes.

📌 This makes high-priority KPIs contribute more to group score.

⸻

🔁 Step 5: Reporting and Tracking

Submissions

Model: kpi.report.submission
	•	Stores each user’s submission per KPI, with:
	•	value, target_value, achievement_percent, note, date
	•	Used for audit and tracking improvement over time.

UI Features
	•	Tree View: KPI list with progress
	•	Form View: Full detail + submission history
	•	Graph & Pivot: Visual dashboards
	•	Search & Grouping: By department, report, KPI type

⸻

🔒 Step 6: Security and Access

Role	Abilities
Admin	Full create/edit/delete for all KPIs and reports
Manager	Can submit manual KPIs; view full group KPIs assigned to their department
User	View only KPIs assigned or part of group they belong to

Rules are enforced via:
	•	Access rights (CSV)
	•	Record rules (domain-based)
	•	View-level restrictions (readonly="not is_admin" etc.)

⸻

⏰ Step 7: Automation & Reminders
	•	Cron Job: Auto refresh all auto KPIs daily
	•	Reminder Button (per group): Sends emails to assigned users to submit manual KPIs
	•	Email Template: kpi_manual_entry_email_template

⸻



Suggested:


Here are suggested improvements and additional features to enhance the current kpi_tracking_v11.6 module functionality, scalability, and user experience:

⸻

✅ Suggested Features & Improvements

⸻

🔧 1. Submission Commenting & Audit Log
	•	Add a comments field or chatter (mail.thread) on kpi.report.submission
	•	Track edits to manual KPI values with timestamp & user
	•	Integrate with the Odoo Auditlog module (you already use it)

✅ Benefit: Increases transparency for manual KPI submissions.

⸻

📊 2. Multi-Level Aggregation Reports
	•	Add department-wise, region-wise or company-wide aggregated views
	•	Allow grouping multiple kpi.report.group into a kpi.dashboard.profile model

✅ Benefit: Helps managers get a bird’s-eye view across locations/teams.

⸻

🧠 3. KPI Trendline Graphs
	•	Visualize kpi.report.submission data over time per KPI
	•	Use plotly or default Odoo graph view with:
	•	Weekly, monthly trend
	•	Performance comparison across users

✅ Benefit: Helps identify progress and seasonality.

⸻

🎯 4. Threshold-Based Alerts
	•	Add min/max thresholds per KPI
	•	Send notifications to assigned users if value deviates critically

✅ Benefit: Proactive alerts on poor performance or unexpected spikes.

⸻

📥 5. Bulk Import Wizard
	•	Add Excel import/export feature to:
	•	Upload multiple manual KPI values
	•	Bulk create KPIs with formulas and domains

✅ Benefit: Saves time for admins managing large data sets.

⸻

🔒 6. Fine-Grained Permission Control
	•	Make manual_value field editable only if:
	•	KPI is manual
	•	kpi.report.assigned_user_ids contains logged-in user
	•	Allow setting per-KPI submission restrictions (e.g., only once per day/week)

✅ Benefit: Prevents unauthorized manual value tampering.

⸻

🧮 7. Custom Scoring Systems
	•	Instead of using only percentage (achievement_percent), allow:
	•	Color-coded score badges
	•	Star-based ratings
	•	Weighted rating formulas (like “Excellent”, “Needs Improvement”)

✅ Benefit: Better understanding of goal alignment at non-numeric levels.

⸻

🛎 8. Submission Deadline Enforcement
	•	Add submission_deadline field in kpi.report
	•	Mark KPIs overdue if not submitted before the deadline

✅ Benefit: Encourages timely manual reporting.

⸻

🧾 9. KPI Templates
	•	Predefine KPI templates per department
	•	Auto-fill domain/formula/target based on selection

✅ Benefit: Standardizes KPI creation across users.

⸻

💡 10. Employee Self KPI View
	•	Add My KPI Dashboard menu:
	•	Shows only KPIs assigned to logged-in user
	•	Clean UI with quick submission and progress

✅ Benefit: Easier navigation for salespersons, store techs, etc.

⸻

🧩 11. Integrate with Goals or OKRs
	•	Map kpi.report to larger goal.objective model
	•	Build parent-child hierarchy of KPI → Goal → Strategy

✅ Benefit: Connects KPIs to business vision/mission.

⸻

Would you like a few of these prioritized and developed for the next version (v11.7)? I can also help you prepare a roadmap or changelog accordingly.

