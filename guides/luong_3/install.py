"""Install the room allocation example when the user runs this in the container."""
import ast
import shutil
from datetime import datetime
from pathlib import Path

source = Path(__file__).resolve().parent
bench = Path("/workspace/development/frappe-bench")
package = bench / "apps/education/education"

module_source = source / "ling_room.py"
ast.parse(module_source.read_text(encoding="utf-8"))
module_destination = package / "ling_room.py"
hooks = package / "hooks.py"
hooks_text = hooks.read_text(encoding="utf-8")
marker = "# BEGIN LING IELTS ROOM GUIDE"
hook_path = "education.ling_room.validate_course_schedule_room"
snippet = '''

# BEGIN LING IELTS ROOM GUIDE
doc_events = globals().get("doc_events") or {}
_ling_room_course_events = doc_events.setdefault("Course Schedule", {})
_ling_room_validators = _ling_room_course_events.get("validate", [])
if isinstance(_ling_room_validators, str):
    _ling_room_validators = [_ling_room_validators]
if "education.ling_room.validate_course_schedule_room" not in _ling_room_validators:
    _ling_room_validators = [*_ling_room_validators, "education.ling_room.validate_course_schedule_room"]
_ling_room_course_events["validate"] = _ling_room_validators
# END LING IELTS ROOM GUIDE
'''
new_hooks = hooks_text
if marker not in hooks_text and hook_path not in hooks_text:
    new_hooks = hooks_text + snippet
ast.parse(new_hooks)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
backup = bench / "sites/school.localhost/private/code_backups" / f"room_code_{stamp}"
backup.mkdir(parents=True, exist_ok=False)
shutil.copy2(hooks, backup / "hooks.py")
if module_destination.exists():
    shutil.copy2(module_destination, backup / "ling_room.py")

shutil.copy2(module_source, module_destination)
hooks.write_text(new_hooks, encoding="utf-8")
print(f"Đã cài {module_destination}")
print(f"Đã đăng ký hook kiểm tra loại phòng cho Course Schedule. Bản sao mã trước thay đổi: {backup}")
print("Tiếp theo chạy bench clear-cache, restart frappe và tạo Client Script theo README.")
