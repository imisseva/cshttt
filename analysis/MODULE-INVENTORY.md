# Kiểm kê đầy đủ module và DocType — 08/11/2026

Nguồn: modules.txt và các file định nghĩa DocType của ba app đang cài. Tên giữ nguyên để đối chiếu giao diện/mã nguồn. Số lượng bao gồm bảng con, Single và công cụ; không phải số module nghiệp vụ độc lập.

| # | Module kỹ thuật ERPNext | DocType* | Chức năng | Ánh xạ Ling IELTS |
|---|---|---:|---|---|
| 1 | Accounts | 191 | Kế toán, hóa đơn, thanh toán | Trực tiếp: học phí, công nợ, Sales Invoice/Payment Entry |
| 2 | CRM | 28 | Khách hàng tiềm năng, cơ hội, chiến dịch | Có thể dùng tư vấn tuyển sinh; chưa bắt buộc trong 7 luồng |
| 3 | Buying | 20 | Mua hàng, nhà cung cấp | Ngoài phạm vi A1 |
| 4 | Projects | 15 | Dự án, công việc, chấm thời gian | Có thể quản lý việc nội bộ; không dùng thay lớp học |
| 5 | Selling | 20 | Khách hàng, chào giá, đơn bán | Tái sử dụng Customer, cấu hình bán/giảm giá; luồng học phí chính ở Accounts + Education |
| 6 | Setup | 40 | Công ty, kỳ nghỉ, cấu hình tổ chức | Dữ liệu nền cho kế toán và lịch nghỉ |
| 7 | Manufacturing | 50 | Sản xuất, định mức, lệnh sản xuất | Ngoài phạm vi A1 |
| 8 | Stock | 76 | Kho, vật tư, luân chuyển tồn kho | Ngoài phạm vi; Item có thể dùng làm mã khoản thu |
| 9 | Support | 11 | Yêu cầu hỗ trợ, xử lý sự cố | Ngoài phạm vi A1 |
| 10 | Utilities | 4 | Tiện ích nghiệp vụ dùng chung | Hỗ trợ kỹ thuật, không phải một luồng IELTS |
| 11 | Assets | 26 | Tài sản cố định | Tùy chọn quản lý thiết bị phòng học; ngoài Must |
| 12 | Portal | 2 | Chức năng portal phía ERPNext | Không đồng nhất với cổng học viên của Education |
| 13 | Maintenance | 5 | Lịch và tác vụ bảo trì | Ngoài phạm vi A1 |
| 14 | Regional | 5 | Thiết lập nghiệp vụ theo khu vực | Không coi là bộ đáp ứng pháp lý/kế toán Việt Nam đã được kiểm định |
| 15 | ERPNext Integrations | 1 | Tích hợp của ERPNext | Không có tích hợp Zalo sẵn cho yêu cầu này |
| 16 | Quality Management | 16 | Mục tiêu, quy trình và đánh giá chất lượng | Không thay thế Assessment Result học viên |
| 17 | Communication | 2 | Đối tượng phục vụ giao tiếp của ERPNext | Không đồng nghĩa đã cấu hình thông báo 7 luồng |
| 18 | Telephony | 5 | Nhật ký và tích hợp điện thoại | Ngoài phạm vi A1 |
| 19 | Bulk Transaction | 2 | Thao tác chứng từ hàng loạt | Tiện ích, không phải nghiệp vụ lớp học |
| 20 | Subcontracting | 13 | Gia công thuê ngoài | Ngoài phạm vi A1 |
| 21 | EDI | 2 | Trao đổi dữ liệu điện tử | Ngoài phạm vi A1 |

## Education — toàn bộ 76 DocType

| # | DocType | Loại | Nguồn |
|---|---|---|---|
| 1 | Academic Term | Tài liệu thường | Education gốc |
| 2 | Academic Year | Tài liệu thường | Education gốc |
| 3 | Article | Tài liệu thường | Education gốc |
| 4 | Assessment Criteria | Tài liệu thường | Education gốc |
| 5 | Assessment Criteria Group | Tài liệu thường | Education gốc |
| 6 | Assessment Group | Tài liệu thường | Education gốc |
| 7 | Assessment Plan | Tài liệu thường | Education gốc |
| 8 | Assessment Plan Criteria | Bảng con | Education gốc |
| 9 | Assessment Result | Tài liệu thường | Education gốc |
| 10 | Assessment Result Detail | Bảng con | Education gốc |
| 11 | Assessment Result Tool | Single/công cụ cấu hình | Education gốc |
| 12 | Course | Tài liệu thường | Education gốc |
| 13 | Course Activity | Tài liệu thường | Education gốc |
| 14 | Course Assessment Criteria | Bảng con | Education gốc |
| 15 | Course Enrollment | Tài liệu thường | Education gốc |
| 16 | Course Schedule | Tài liệu thường | Education gốc |
| 17 | Course Scheduling Tool | Single/công cụ cấu hình | Education gốc |
| 18 | Course Topic | Bảng con | Education gốc |
| 19 | doct | Tài liệu thường | Dự án |
| 20 | Education Settings | Single/công cụ cấu hình | Education gốc |
| 21 | Fee Category | Tài liệu thường | Education gốc |
| 22 | Fee Category Default | Bảng con | Education gốc |
| 23 | Fee Component | Bảng con | Education gốc |
| 24 | Fee Schedule | Tài liệu thường | Education gốc |
| 25 | Fee Schedule Details | Bảng con | Education gốc |
| 26 | Fee Schedule Program | Bảng con | Education gốc |
| 27 | Fee Schedule Student Group | Bảng con | Education gốc |
| 28 | Fee Structure | Tài liệu thường | Education gốc |
| 29 | Fees | Tài liệu thường | Education gốc |
| 30 | Grading Scale | Tài liệu thường | Education gốc |
| 31 | Grading Scale Interval | Bảng con | Education gốc |
| 32 | Guardian | Tài liệu thường | Education gốc |
| 33 | Guardian Interest | Bảng con | Education gốc |
| 34 | Guardian Student | Bảng con | Education gốc |
| 35 | Instructor | Tài liệu thường | Education gốc |
| 36 | Instructor Log | Bảng con | Education gốc |
| 37 | Level Transfer Request | Tài liệu thường | Dự án |
| 38 | Options | Bảng con | Education gốc |
| 39 | Payment Record | Tài liệu thường | Education gốc |
| 40 | Program | Tài liệu thường | Education gốc |
| 41 | Program Course | Bảng con | Education gốc |
| 42 | Program Enrollment | Tài liệu thường | Education gốc |
| 43 | Program Enrollment Course | Bảng con | Education gốc |
| 44 | Program Enrollment Fee | Bảng con | Education gốc |
| 45 | Program Enrollment Tool | Single/công cụ cấu hình | Education gốc |
| 46 | Program Enrollment Tool Student | Bảng con | Education gốc |
| 47 | Program Fee | Bảng con | Education gốc |
| 48 | Question | Tài liệu thường | Education gốc |
| 49 | Quiz | Tài liệu thường | Education gốc |
| 50 | Quiz Activity | Tài liệu thường | Education gốc |
| 51 | Quiz Question | Bảng con | Education gốc |
| 52 | Quiz Result | Bảng con | Education gốc |
| 53 | Room | Tài liệu thường | Education gốc |
| 54 | School House | Tài liệu thường | Education gốc |
| 55 | Student | Tài liệu thường | Education gốc |
| 56 | Student Admission | Tài liệu thường | Education gốc |
| 57 | Student Admission Program | Bảng con | Education gốc |
| 58 | Student Applicant | Tài liệu thường | Education gốc |
| 59 | Student Attendance | Tài liệu thường | Education gốc |
| 60 | Student Attendance Tool | Single/công cụ cấu hình | Education gốc |
| 61 | Student Batch Name | Tài liệu thường | Education gốc |
| 62 | Student Category | Tài liệu thường | Education gốc |
| 63 | Student Group | Tài liệu thường | Education gốc |
| 64 | Student Group Creation Tool | Single/công cụ cấu hình | Education gốc |
| 65 | Student Group Creation Tool Course | Bảng con | Education gốc |
| 66 | Student Group Instructor | Bảng con | Education gốc |
| 67 | Student Group Student | Bảng con | Education gốc |
| 68 | Student Guardian | Bảng con | Education gốc |
| 69 | Student Language | Tài liệu thường | Education gốc |
| 70 | Student Leave Application | Tài liệu thường | Education gốc |
| 71 | Student Log | Tài liệu thường | Education gốc |
| 72 | Student Report Generation Tool | Single/công cụ cấu hình | Education gốc |
| 73 | Student Sibling | Bảng con | Education gốc |
| 74 | Student Siblings | Bảng con | Education gốc |
| 75 | Topic | Tài liệu thường | Education gốc |
| 76 | Topic Content | Bảng con | Education gốc |

## Education — toàn bộ report trong mã nguồn

- `absent_student_report`
- `assessment_plan_status`
- `course_wise_assessment_report`
- `final_assessment_grades`
- `program_wise_fee_collection`
- `student_and_guardian_contact_details`
- `student_batch_wise_attendance`
- `student_fee_collection`
- `student_monthly_attendance_sheet`

## frappe — toàn bộ tên DocType theo module

SHA `3d1284c5fdb52207a516a49bbf2fd186cb43b3ab`; 301 định nghĩa.

### Core (105)

Access Log; Activity Log; Amended Document Naming Settings; API Request Log; Audit Trail; Block Module; Comment; Communication; Communication Link; Custom DocPerm; Custom Role; Data Export; Data Import; Data Import Log; Data Import Skipped Row; Data Import Value Mapping; DefaultValue; Deleted Document; DocField; DocPerm; DocShare; DocType; DocType Action; DocType Link; DocType Settings Map; DocType Settings Map Item; DocType State; Doctype To Sync; Document Naming Rule; Document Naming Rule Condition; Document Naming Settings; Document Share Key; Domain; Domain Settings; DuckDB Sync; DuckDB Sync Item; Dynamic Link; Error Log; File; Has Domain; Has Role; Installed Application; Installed Applications; Language; Log Setting User; Log Settings; Logs To Clear; Module Def; Module Profile; Navbar Item; Navbar Settings; Package; Package Import; Package Release; Page; Patch Log; Permission Inspector; Permission Log; Permission Type; Prepared Report; Recorder; Recorder Event; Recorder Query; Recorder Suggested Index; Report; Report Column; Report Filter; Role; Role Permission for Page and Report; Role Profile; RQ Job; RQ Worker; Scheduled Job Log; Scheduled Job Type; Scheduler Event; Security Settings; Security Settings Contact; Security Settings Language; Server Script; Session Default; Session Default Settings; SMS Log; SMS Parameter; SMS Settings; Submission Queue; Success Action; System Settings; Translation; User; User Document Type; User Email; User Group; User Group Member; User Invitation; User Permission; User Role; User Role Profile; User Select Document Type; User Session Display; User Social Login; User Type; User Type Module; User Workspaces; Version; View Log

### Website (39)

About Us Settings; About Us Team Member; Color; Company History; Contact Us Settings; Discussion Reply; Discussion Topic; Help Article; Help Category; Personal Data Deletion Request; Personal Data Deletion Step; Personal Data Download Request; Portal Menu Item; Portal Settings; Social Link Settings; Top Bar Item; UTM Campaign; UTM Medium; UTM Source; Web Form; Web Form Field; Web Form List Column; Web Form Request; Web Page; Web Page Block; Web Page View; Web Template; Web Template Field; Website Meta Tag; Website Route Meta; Website Route Redirect; Website Script; Website Settings; Website Sidebar; Website Sidebar Item; Website Slideshow; Website Slideshow Item; Website Theme; Website Theme Ignore App

### Workflow (9)

Workflow; Workflow Action; Workflow Action Master; Workflow Action Permitted Role; Workflow Document State; Workflow State; Workflow Transition; Workflow Transition Task; Workflow Transition Tasks

### Email (17)

Auto Email Report; Document Follow; Email Account; Email Domain; Email Flag Queue; Email Group; Email Group Member; Email Queue; Email Queue Recipient; Email Rule; Email Template; Email Unsubscribe; IMAP Folder; Notification; Notification Recipient; Reply To Address; Unhandled Email

### Custom (7)

Client Script; Custom Field; Customize Form; Customize Form Field; DocType Layout; DocType Layout Field; Property Setter

### Geo (2)

Country; Currency

### Desk (67)

Bulk Update; Calendar View; Console Log; Custom HTML Block; Custom Sidebar; Custom Workspace; Dashboard; Dashboard Chart; Dashboard Chart Field; Dashboard Chart Link; Dashboard Chart Source; Dashboard Settings; Desktop Icon; Desktop Layout; Desktop Settings; Dock; Dock Item; Event; Event Notifications; Event Participants; Form Tour; Form Tour Step; Global Search DocType; Global Search Settings; Kanban Board; Kanban Board Column; Kanban Board Field; Kanban Board Group Field; List Filter; List View Settings; Module Onboarding; Note; Note Seen By; Notification Log; Notification Settings; Notification Subscribed Document; Notification Type; Notification Type Preference; Number Card; Number Card Link; Onboarding Permission; Onboarding Step; Onboarding Step Map; Route History; Sidebar; Sidebar Item; Sidebar Item Group; Sidebar Item Group Link; System Console; System Health Report; System Health Report Errors; System Health Report Failing Jobs; System Health Report Queue; System Health Report Tables; System Health Report Workers; Tag; Tag Link; ToDo; Workspace; Workspace Chart; Workspace Custom Block; Workspace Link; Workspace Number Card; Workspace Quick List; Workspace Shortcut; Workspace Sidebar; Workspace Sidebar Item

### Integrations (24)

Connected App; Geolocation Settings; Google Calendar; Google Contacts; Google Settings; Integration Request; LDAP Group Mapping; LDAP Settings; OAuth Authorization Code; OAuth Bearer Token; OAuth Client; OAuth Client Role; OAuth Provider Settings; OAuth Scope; OAuth Settings; Push Notification Settings; Query Parameters; Slack Webhook URL; Social Login Key; Token Cache; Webhook; Webhook Data; Webhook Header; Webhook Request Log

### Printing (8)

Letter Head; Network Printer Settings; Print Format; Print Format Field Template; Print Format Snippet; Print Heading; Print Settings; Print Style

### Contacts (7)

Address; Address Template; Contact; Contact Email; Contact Phone; Gender; Salutation

### Automation (16)

Assignment Rule; Assignment Rule Day; Assignment Rule User; Auto Repeat; Auto Repeat Day; Auto Repeat User; Automation Action; Automation Event Subscription; Automation Flow; Automation Run; Automation Run Step; Automation Settings; Automation Trigger Queue; Milestone; Milestone Tracker; Reminder

### System (0)

(Không có định nghĩa DocType trong phạm vi kiểm kê.)

### Build (0)

(Không có định nghĩa DocType trong phạm vi kiểm kê.)

### Data (0)

(Không có định nghĩa DocType trong phạm vi kiểm kê.)

### Users (0)

(Không có định nghĩa DocType trong phạm vi kiểm kê.)

## erpnext — toàn bộ tên DocType theo module

SHA `495380b59c8701629f25089bd3807e6ddf7f26c6`; 534 định nghĩa.

### Accounts (191)

Account; Account Category; Account Closing Balance; Accounting Dimension; Accounting Dimension Detail; Accounting Dimension Filter; Accounting Period; Accounts Settings; Advance Payment Ledger Entry; Advance Taxes and Charges; Allowed Dimension; Allowed To Transact With; Applicable On Account; Bank; Bank Account; Bank Account Balance; Bank Account Subtype; Bank Account Type; Bank Clearance; Bank Clearance Detail; Bank Guarantee; Bank Reconciliation Tool; Bank Statement Import; Bank Statement Import Log; Bank Statement Import Log Column Map; Bank Transaction; Bank Transaction Mapping; Bank Transaction Payments; Bank Transaction Rule; Bank Transaction Rule Accounts; Bank Transaction Rule Description Conditions; Bisect Accounting Statements; Bisect Nodes; Budget; Budget Account; Budget Distribution; Campaign Item; Cashier Closing; Cashier Closing Payments; Chart of Accounts Importer; Cheque Print Template; Closed Document; Cost Center; Cost Center Allocation; Cost Center Allocation Percentage; Coupon Code; Currency Exchange Settings; Currency Exchange Settings Details; Currency Exchange Settings Result; Customer Group Item; Customer Item; Discounted Invoice; Dunning; Dunning Letter Text; Dunning Type; Exchange Rate Revaluation; Exchange Rate Revaluation Account; Finance Book; Financial Report Row; Financial Report Template; Fiscal Year; Fiscal Year Company; GL Entry; Invoice Discounting; Item Tax Template; Item Tax Template Detail; Item Wise Tax Detail; Journal Entry; Journal Entry Account; Journal Entry Template; Journal Entry Template Account; Ledger Health; Ledger Health Monitor; Ledger Health Monitor Company; Ledger Merge; Ledger Merge Accounts; Loyalty Point Entry; Loyalty Point Entry Redemption; Loyalty Program; Loyalty Program Collection; Mode of Payment; Mode of Payment Account; Monthly Distribution; Monthly Distribution Percentage; Opening Invoice Creation Tool; Opening Invoice Creation Tool Item; Overdue Payment; Party Account; Party Link; Payment Entry; Payment Entry Deduction; Payment Entry Reference; Payment Gateway Account; Payment Ledger Entry; Payment Order; Payment Order Reference; Payment Reconciliation; Payment Reconciliation Allocation; Payment Reconciliation Invoice; Payment Reconciliation Payment; Payment Reference; Payment Request; Payment Schedule; Payment Term; Payment Terms Template; Payment Terms Template Detail; Pegged Currencies; Pegged Currency Details; Period Closing Voucher; POS Closing Entry; POS Closing Entry Detail; POS Closing Entry Taxes; POS Customer Group; POS Field; POS Invoice; POS Invoice Item; POS Invoice Merge Log; POS Invoice Reference; POS Item Group; POS Opening Entry; POS Opening Entry Detail; POS Payment Method; POS Profile; POS Profile User; POS Search Fields; POS Settings; Pricing Rule; Pricing Rule Brand; Pricing Rule Detail; Pricing Rule Item Code; Pricing Rule Item Group; Process Deferred Accounting; Process Payment Reconciliation; Process Payment Reconciliation Log; Process Payment Reconciliation Log Allocations; Process Period Closing Voucher; Process Period Closing Voucher Detail; Process Statement Of Accounts; Process Statement Of Accounts CC; Process Statement Of Accounts Customer; Process Subscription; Promotional Scheme; Promotional Scheme Price Discount; Promotional Scheme Product Discount; PSOA Cost Center; PSOA Project; Purchase Invoice; Purchase Invoice Advance; Purchase Invoice Item; Purchase Taxes and Charges; Purchase Taxes and Charges Template; Repost Accounting Ledger; Repost Accounting Ledger Items; Repost Allowed Types; Repost Payment Ledger; Repost Payment Ledger Items; Sales Invoice; Sales Invoice Advance; Sales Invoice Item; Sales Invoice Payment; Sales Invoice Reference; Sales Invoice Timesheet; Sales Partner Item; Sales Taxes and Charges; Sales Taxes and Charges Template; Share Balance; Share Transfer; Share Type; Shareholder; Shipping Rule; Shipping Rule Condition; Shipping Rule Country; South Africa VAT Account; Subscription; Subscription Invoice; Subscription Plan; Subscription Plan Detail; Subscription Settings; Supplier Group Item; Supplier Item; Tax Category; Tax Rule; Tax Withholding Account; Tax Withholding Category; Tax Withholding Entry; Tax Withholding Group; Tax Withholding Rate; Territory Item; Transaction Deletion Record Details; Unreconcile Payment; Unreconcile Payment Entries

### CRM (28)

Appointment; Appointment Booking Settings; Appointment Booking Slots; Availability Of Slots; Campaign; Campaign Email Schedule; Competitor; Competitor Detail; Contract; Contract Fulfilment Checklist; Contract Template; Contract Template Fulfilment Terms; CRM Note; CRM Settings; Email Campaign; Frappe CRM Allowed User; Lead; Lost Reason Detail; Market Segment; Opportunity; Opportunity Item; Opportunity Lost Reason; Opportunity Lost Reason Detail; Opportunity Type; Prospect; Prospect Lead; Prospect Opportunity; Sales Stage

### Buying (20)

Buying Settings; Customer Number At Supplier; Purchase Order; Purchase Order Item; Purchase Order Item Supplied; Purchase Receipt Item Supplied; Request for Quotation; Request for Quotation Item; Request for Quotation Supplier; Supplier; Supplier Quotation; Supplier Quotation Item; Supplier Scorecard; Supplier Scorecard Criteria; Supplier Scorecard Period; Supplier Scorecard Scoring Criteria; Supplier Scorecard Scoring Standing; Supplier Scorecard Scoring Variable; Supplier Scorecard Standing; Supplier Scorecard Variable

### Projects (15)

Activity Cost; Activity Type; Dependent Task; Project; Project Template; Project Template Task; Project Type; Project Update; Project User; Projects Settings; Task; Task Depends On; Task Type; Timesheet; Timesheet Detail

### Selling (20)

Customer; Customer Credit Limit; Delivery Schedule Item; Industry Type; Installation Note; Installation Note Item; Party Specific Item; Product Bundle; Product Bundle Item; Proforma Invoice; Proforma Invoice Item; Quotation; Quotation Item; Sales Order; Sales Order Item; Sales Partner Type; Sales Team; Selling Settings; SMS Center; Supplier Number At Customer

### Setup (40)

Authorization Control; Authorization Rule; Branch; Brand; Company; Currency Exchange; Customer Group; Department; Designation; Driver; Driving License Category; Email Digest; Email Digest Recipient; Employee; Employee Education; Employee External Work History; Employee Group; Employee Group Table; Employee Internal Work History; Global Defaults; Holiday; Holiday List; Incoterm; Item Group; Party Type; Quotation Lost Reason; Quotation Lost Reason Detail; Sales Partner; Sales Person; Supplier Group; Target Detail; Terms and Conditions; Territory; Transaction Deletion Record; Transaction Deletion Record Item; Transaction Deletion Record To Delete; UOM; UOM Conversion Factor; Vehicle; Website Item Group

### Manufacturing (50)

Blanket Order; Blanket Order Item; BOM; BOM Creator; BOM Creator Item; BOM Creator Material; BOM Creator Operation; BOM Explosion Item; BOM Item; BOM Operation; BOM Secondary Item; BOM Update Batch; BOM Update Log; BOM Update Tool; BOM Website Item; BOM Website Operation; Downtime Entry; Job Card; Job Card Item; Job Card Operation; Job Card Scheduled Time; Job Card Secondary Item; Job Card Time Log; Manufacturing Settings; Master Production Schedule; Master Production Schedule Item; Material Request Plan Item; Operation; Plant Floor; Production Plan; Production Plan Item; Production Plan Item Reference; Production Plan Material Request; Production Plan Material Request Warehouse; Production Plan Sales Order; Production Plan Sub Assembly Item; Routing; Sales Forecast; Sales Forecast Item; Sub Operation; Work Order; Work Order Additional Item; Work Order Item; Work Order Operation; Workstation; Workstation Cost; Workstation Operating Component; Workstation Operating Component Account; Workstation Type; Workstation Working Hour

### Stock (76)

Batch; Bin; Company Restriction; Customs Tariff Number; Delivery Note; Delivery Note Item; Delivery Settings; Delivery Stop; Delivery Trip; Inventory Dimension; Item; Item Alternative; Item Attribute; Item Attribute Value; Item Barcode; Item Customer Detail; Item Default; Item Lead Time; Item Manufacturer; Item Price; Item Quality Inspection Parameter; Item Reorder; Item Supplier; Item Tax; Item Variant; Item Variant Attribute; Item Variant Settings; Item Website Specification; Landed Cost Item; Landed Cost Purchase Receipt; Landed Cost Taxes and Charges; Landed Cost Vendor Invoice; Landed Cost Voucher; Manufacturer; Material Request; Material Request Item; Packed Item; Packing Slip; Packing Slip Item; Pick List; Pick List Item; Price List; Price List Country; Purchase Receipt; Purchase Receipt Item; Putaway Rule; Quality Inspection; Quality Inspection Parameter; Quality Inspection Parameter Group; Quality Inspection Reading; Quality Inspection Template; Quick Stock Balance; Repost Item Valuation; Serial and Batch Bundle; Serial and Batch Entry; Serial No; Shipment; Shipment Delivery Note; Shipment Parcel; Shipment Parcel Template; Stock Closing Balance; Stock Closing Entry; Stock Entry; Stock Entry Detail; Stock Entry Type; Stock Ledger Entry; Stock Reconciliation; Stock Reconciliation Item; Stock Reposting Settings; Stock Reservation Entry; Stock Settings; UOM Category; UOM Conversion Detail; Variant Field; Warehouse; Warehouse Type

### Support (11)

Issue; Issue Priority; Issue Type; Pause SLA On Status; Service Day; Service Level Agreement; Service Level Priority; SLA Fulfilled On Status; Support Search Source; Support Settings; Warranty Claim

### Utilities (4)

Portal User; Rename Tool; Video; Video Settings

### Assets (26)

Asset; Asset Activity; Asset Capitalization; Asset Capitalization Asset Item; Asset Capitalization Service Item; Asset Capitalization Stock Item; Asset Category; Asset Category Account; Asset Depreciation Schedule; Asset Finance Book; Asset Maintenance; Asset Maintenance Log; Asset Maintenance Task; Asset Maintenance Team; Asset Movement; Asset Movement Item; Asset Repair; Asset Repair Consumed Item; Asset Repair Purchase Invoice; Asset Shift Allocation; Asset Shift Factor; Asset Value Adjustment; Depreciation Schedule; Linked Location; Location; Maintenance Team Member

### Portal (2)

Website Attribute; Website Filter Field

### Maintenance (5)

Maintenance Schedule; Maintenance Schedule Detail; Maintenance Schedule Item; Maintenance Visit; Maintenance Visit Purpose

### Regional (5)

Import Supplier Invoice; Lower Deduction Certificate; South Africa VAT Settings; UAE VAT Account; UAE VAT Settings

### ERPNext Integrations (1)

Plaid Settings

### Quality Management (16)

Non Conformance; Quality Action; Quality Action Resolution; Quality Feedback; Quality Feedback Parameter; Quality Feedback Template; Quality Feedback Template Parameter; Quality Goal; Quality Goal Objective; Quality Meeting; Quality Meeting Agenda; Quality Meeting Minutes; Quality Procedure; Quality Procedure Process; Quality Review; Quality Review Objective

### Communication (2)

Communication Medium; Communication Medium Timeslot

### Telephony (5)

Call Log; Incoming Call Handling Schedule; Incoming Call Settings; Telephony Call Type; Voice Call Settings

### Bulk Transaction (2)

Bulk Transaction Log; Bulk Transaction Log Detail

### Subcontracting (13)

Subcontracting BOM; Subcontracting Inward Order; Subcontracting Inward Order Item; Subcontracting Inward Order Received Item; Subcontracting Inward Order Secondary Item; Subcontracting Inward Order Service Item; Subcontracting Order; Subcontracting Order Item; Subcontracting Order Service Item; Subcontracting Order Supplied Item; Subcontracting Receipt; Subcontracting Receipt Item; Subcontracting Receipt Supplied Item

### EDI (2)

Code List; Common Code

## Tùy biến quan sát trên site

0 Workflow; 0 Client Script; 0 Server Script. Con số này không bao gồm controller Python/JS viết trong app.

| DocType | Trường custom | Kiểu | Bắt buộc |
|---|---|---|---|
| Student | custom_1 | Data | False |
| Room | custom_room_type | Select | False |
| Sales Order | fee_schedule | Link | False |
| Sales Order | column_break_ejcc | Column Break | False |
| Sales Order | student | Link | False |
| Sales Order | student_info_section | Section Break | False |
| Sales Invoice | fee_schedule | Link | False |
| Sales Invoice | column_break_ejcc | Column Break | False |
| Sales Invoice | student | Link | False |
| Sales Invoice | student_info_section | Section Break | False |
| Communication | company | Link | False |
| Email Account | company | Link | False |
| Contact | is_billing_contact | Check | False |
| Address | is_your_company_address | Check | False |
| Address | tax_category | Link | False |
| UTM Campaign | crm_campaign | Link | False |
| Print Settings | print_taxes_with_zero_amount | Check | False |
| Print Settings | print_uom_after_quantity | Check | False |
| Print Settings | compact_item_print | Check | False |
| DocShare | impersonate | Check | False |
| DocPerm | impersonate | Check | False |
| Custom DocPerm | impersonate | Check | False |
