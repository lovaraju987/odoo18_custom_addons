________________________________________
🔍 Reference: Features in odoo_ess_portal (Third-Party Module)
According to the listing, this paid module includes:
Feature	Description
🧑 Edit Profile	Employees can update their personal info
🕐 Attendance	Portal check-in/check-out
📄 Payslips	View/download salary slips
🗓 Leaves	Apply and track leave status
📊 Timesheets	View submitted hours
📢 Announcements	See internal communications
💰 Expenses	Submit and track reimbursements
________________________________________
✅ How You Can Build a Similar ESS Portal for Free
You already have:
•	Portal access via Odoo Enterprise
•	Community users as employees
•	A clear requirement to avoid paid user licenses
So you can develop an internal version of ESS portal with:
________________________________________
🔧 Functional Features to Implement
Feature	Module Needed	Method	Status
Profile update	hr	Add portal form view (hr.employee)	✅ Implemented
Attendance	hr_attendance	Button: Check-in / Check-out	✅ Implemented
View Payslips	hr_payslip	List/filter payslips by employee_id	✅ Implemented
Leave Requests	hr_holidays	Show approved leaves	❌ Pending
Timesheet View (optional)	project_timesheet	Display read-only timesheets	❌ Pending
Expense Requests (optional)	hr_expense	Submit/view expenses linked to employee	✅ Implemented
________________________________________
🧱 Technical Steps
1.	Custom Module: employee_self_service_portal
o	Extend portal.portal controller
o	Add /my/employee route and submenus
2.	Mapping
o	Link res.users (portal) ↔ hr.employee.user_id
3.	Templates
o	QWeb templates: portal_employee_profile.xml, portal_attendance.xml, etc.
o	Show tabs for each section
4.	Security
o	Add access rules so portal users can:
	Read/write own employee record
	View own payslips, attendances, etc.
5.	Optional Enhancements
o	Add notification for missed check-ins
o	Allow limited profile update (email, phone only)
________________________________________
🧾 Licensing Note
Building it in-house avoids:
•	Paid app fees
•	Dependency on third-party updates
•	Licensing risks if code is modified
________________________________________
