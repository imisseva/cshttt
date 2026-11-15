"""Install the supplied scheduling example when the user runs this in the container."""
import ast
import json
import shutil
from datetime import datetime
from pathlib import Path

source = Path(__file__).resolve().parent
bench = Path("/workspace/development/frappe-bench")
package = bench / "apps/education/education"
metadata_path = package / "education/doctype/instructor_availability/instructor_availability.json"
metadata = json.loads(metadata_path.read_text())
required_fields = {"instructor", "available_date", "from_time", "to_time", "program"}
actual_fields = {field["fieldname"] for field in metadata["fields"]}
if not required_fields <= actual_fields:
    raise RuntimeError(f"Thiếu field trong Instructor Availability: {required_fields - actual_fields}")

module_source = source / "ling_scheduling.py"
ast.parse(module_source.read_text(encoding="utf-8"))
module_destination = package / "ling_scheduling.py"
hooks = package / "hooks.py"
hooks_text = hooks.read_text(encoding="utf-8")
marker = "# BEGIN LING IELTS SCHEDULING GUIDE"
hook_path = "education.ling_scheduling.validate_course_schedule"
snippet = '''

# BEGIN LING IELTS SCHEDULING GUIDE
doc_events = globals().get("doc_events") or {}
_ling_course_events = doc_events.setdefault("Course Schedule", {})
_ling_validators = _ling_course_events.get("validate", [])
if isinstance(_ling_validators, str):
    _ling_validators = [_ling_validators]
if "education.ling_scheduling.validate_course_schedule" not in _ling_validators:
    _ling_validators = [*_ling_validators, "education.ling_scheduling.validate_course_schedule"]
_ling_course_events["validate"] = _ling_validators
# END LING IELTS SCHEDULING GUIDE
'''
new_hooks = hooks_text
if marker not in hooks_text and hook_path not in hooks_text:
    new_hooks = hooks_text + snippet
ast.parse(new_hooks)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
backup = bench / "sites/school.localhost/private/code_backups" / f"scheduling_code_{stamp}"
backup.mkdir(parents=True, exist_ok=False)
shutil.copy2(hooks, backup / "hooks.py")
if module_destination.exists():
    shutil.copy2(module_destination, backup / "ling_scheduling.py")

shutil.copy2(module_source, module_destination)
hooks.write_text(new_hooks, encoding="utf-8")
print(f"Đã cài {module_destination}")
print(f"Đã đăng ký hook kiểm tra Course Schedule. Bản sao mã trước thay đổi: {backup}")
print("Tiếp theo chạy bench clear-cache, restart frappe và tạo Client Script theo README.")
