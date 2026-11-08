param(
    [string]$message = "update customizations and doctypes"
)

Write-Host "📦 1. Dang tu dong quet cac DocType moi va Customizations..." -ForegroundColor Cyan

# Danh sach cac DocType goc cua Frappe Education (khong can copy)
$standardDocTypes = @(
    "academic_term", "academic_year", "article", "assessment_criteria", "assessment_criteria_group",
    "assessment_group", "assessment_plan", "assessment_plan_criteria", "assessment_result",
    "assessment_result_detail", "assessment_result_tool", "course", "course_activity",
    "course_assessment_criteria", "course_enrollment", "course_schedule", "course_scheduling_tool",
    "course_topic", "education_settings", "fees", "fee_category", "fee_category_default",
    "fee_component", "fee_schedule", "fee_schedule_details", "fee_schedule_program",
    "fee_schedule_student_group", "fee_structure", "grading_scale", "grading_scale_interval",
    "guardian", "guardian_interest", "guardian_student", "instructor", "instructor_log",
    "options", "payment_record", "program", "program_course", "program_enrollment",
    "program_enrollment_course", "program_enrollment_fee", "program_enrollment_tool",
    "program_enrollment_tool_student", "program_fee", "question", "quiz", "quiz_activity",
    "quiz_question", "quiz_result", "room", "school_house", "student", "student_admission",
    "student_admission_program", "student_applicant", "student_attendance", "student_attendance_tool",
    "student_batch_name", "student_category", "student_group", "student_group_creation_tool",
    "student_group_creation_tool_course", "student_group_instructor", "student_group_student",
    "student_guardian", "student_language", "student_leave_application", "student_log",
    "student_report_generation_tool", "student_sibling", "student_siblings", "topic",
    "topic_content", "__pycache__"
)

$sourceDocTypes = "frappe_docker\development\frappe-bench\apps\education\education\education\doctype"
New-Item -ItemType Directory -Force -Path custom_doctypes\custom | Out-Null

# 1. Tu dong quet va copy bat ky DocType moi nao duoc tao ra
if (Test-Path $sourceDocTypes) {
    Get-ChildItem -Directory -Path $sourceDocTypes | ForEach-Object {
        $folderName = $_.Name
        if ($standardDocTypes -notcontains $folderName) {
            Write-Host "  -> Phat hien Custom DocType: $folderName" -ForegroundColor Yellow
            $target = "custom_doctypes\$folderName"
            New-Item -ItemType Directory -Force -Path $target | Out-Null
            Copy-Item -Recurse -Force "$($_.FullName)\*" $target\
            Remove-Item -Recurse -Force "$target\__pycache__" -ErrorAction SilentlyContinue
        }
    }
}

# 2. Tu dong copy tat ca cac file Customization json (Export Customizations)
$customSource = "frappe_docker\development\frappe-bench\apps\education\education\education\custom"
if (Test-Path $customSource) {
    Copy-Item -Recurse -Force "$customSource\*" custom_doctypes\custom\
}

Write-Host "🚀 2. Dang day len GitHub..." -ForegroundColor Cyan
git add custom_doctypes README.md push.ps1 pull.ps1
git commit -m $message
git push origin main

Write-Host "✅ Da day len GitHub thanh cong voi thong diep: '$message'" -ForegroundColor Green
