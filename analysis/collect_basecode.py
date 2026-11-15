"""Read-only source and schema inventory for the Ling IELTS gap analysis."""
import json
import os
import pathlib
import shutil
import subprocess
import sys

bench = pathlib.Path('/workspace/development/frappe-bench')
out = pathlib.Path('/tmp/ling-erpnext-audit')
out.mkdir(exist_ok=True)
snapshot = {'apps': {}, 'source_files': []}
selected_education = {
    'student', 'guardian', 'student_applicant', 'program', 'program_enrollment',
    'student_group', 'instructor', 'room', 'course_schedule', 'course_scheduling_tool',
    'student_attendance', 'student_attendance_tool', 'student_leave_application',
    'assessment_plan', 'assessment_result', 'assessment_result_tool', 'assessment_criteria',
    'grading_scale', 'fee_structure', 'fee_schedule', 'fees', 'education_settings',
    'level_transfer_request', 'doct',
}
selected_erpnext = {'sales_invoice', 'payment_entry', 'sales_order', 'pricing_rule'}
framework_paths = {
    'frappe/model/document.py', 'frappe/permissions.py', 'frappe/model/base_document.py',
    'frappe/migrate.py', 'frappe/model/workflow.py',
    'frappe/custom/doctype/customize_form/customize_form.py',
    'frappe/core/doctype/doctype/doctype.py',
}

def copy_source(app, root, path):
    relative = path.relative_to(root)
    destination = out / 'source' / app / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(path, destination)
    snapshot['source_files'].append(f'{app}/{relative.as_posix()}')

for app in ('frappe', 'erpnext', 'education'):
    root = bench / 'apps' / app
    app_package = root / app
    info = {'sha': subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip(),
            'modules': (app_package / 'modules.txt').read_text().splitlines(), 'doctypes': []}
    for path in sorted(app_package.glob('**/doctype/*/*.json')):
        if path.parent.name != path.stem:
            continue
        data = json.loads(path.read_text())
        if data.get('doctype') != 'DocType':
            continue
        item = {key: data.get(key) for key in ('name', 'module', 'istable', 'issingle', 'is_submittable', 'custom', 'autoname', 'track_changes')}
        item['path'] = path.relative_to(root).as_posix()
        if app == 'education' or path.stem in selected_erpnext:
            item['fields'] = data.get('fields', [])
            item['permissions'] = data.get('permissions', [])
        info['doctypes'].append(item)
        selected = app == 'education' and path.stem in selected_education or app == 'erpnext' and path.stem in selected_erpnext
        if selected:
            for suffix in ('.json', '.py', '.js'):
                source = path.with_suffix(suffix)
                if source.exists():
                    copy_source(app, root, source)
    for relative in (f'{app}/modules.txt', f'{app}/hooks.py', 'pyproject.toml'):
        path = root / relative
        if path.exists():
            copy_source(app, root, path)
    if app == 'frappe':
        for relative in framework_paths:
            copy_source(app, root, root / relative)
    if app == 'education':
        for relative in ('education/utils.py', 'education/api.py', 'education/education/utils.py', 'education/education/api.py', 'education/education/__init__.py'):
            path = root / relative
            if path.exists():
                copy_source(app, root, path)
        for folder in ('education/api', 'education/report'):
            for path in sorted((root / folder).rglob('*.py')):
                copy_source(app, root, path)
        for path in sorted((root/'frontend'/'src').rglob('*')):
            if path.is_file() and path.suffix in ('.vue', '.js', '.ts'):
                copy_source(app, root, path)
        info['reports'] = [p.parent.name for p in sorted(app_package.glob('**/report/*/*.json')) if p.stem == p.parent.name]
        info['portal_routes'] = [p.relative_to(root).as_posix() for p in sorted((app_package/'www').rglob('*')) if p.is_file()]
    snapshot['apps'][app] = info

sys.path.insert(0, str(bench / 'apps' / 'frappe'))
import frappe
os.chdir(bench / 'sites')
frappe.init(site='school.localhost', sites_path=str(bench / 'sites'))
frappe.connect()
snapshot['site'] = {
    'doctypes': frappe.get_all('DocType', fields=['name', 'module', 'custom', 'istable', 'issingle', 'is_submittable']),
    'custom_fields': frappe.get_all('Custom Field', fields=['dt', 'fieldname', 'fieldtype', 'options', 'reqd']),
    'workflows': frappe.get_all('Workflow', fields=['name', 'document_type', 'is_active']),
    'client_scripts': frappe.get_all('Client Script', fields=['name', 'dt', 'enabled']),
    'server_scripts': frappe.get_all('Server Script', fields=['name', 'reference_doctype', 'disabled']),
}
frappe.destroy()
(out / 'inventory.json').write_text(json.dumps(snapshot, ensure_ascii=False, indent=2, default=str))
print(json.dumps({'apps': {k: {'sha': v['sha'], 'modules': v['modules'], 'doctype_count': len(v['doctypes'])} for k,v in snapshot['apps'].items()}, 'site': {k: len(v) for k,v in snapshot['site'].items()}, 'copied_source_files': len(snapshot['source_files'])}, ensure_ascii=False, indent=2))
