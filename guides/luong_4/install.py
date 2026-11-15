"""Install the fee payment validation when the user runs this in the container."""
import ast
import shutil
from datetime import datetime
from pathlib import Path

source = Path(__file__).resolve().parent
bench = Path("/workspace/development/frappe-bench")
package = bench / "apps/education/education"

module_source = source / "ling_fees.py"
ast.parse(module_source.read_text(encoding="utf-8"))
module_destination = package / "ling_fees.py"
hooks = package / "hooks.py"
hooks_text = hooks.read_text(encoding="utf-8")
marker = "# BEGIN LING IELTS FEES GUIDE"
hook_path = "education.ling_fees.validate_student_group_fees"
snippet = '''

# BEGIN LING IELTS FEES GUIDE
doc_events = globals().get("doc_events") or {}
_ling_fee_group_events = doc_events.setdefault("Student Group", {})
_ling_fee_validators = _ling_fee_group_events.get("validate", [])
if isinstance(_ling_fee_validators, str):
    _ling_fee_validators = [_ling_fee_validators]
if "education.ling_fees.validate_student_group_fees" not in _ling_fee_validators:
    _ling_fee_validators = [*_ling_fee_validators, "education.ling_fees.validate_student_group_fees"]
_ling_fee_group_events["validate"] = _ling_fee_validators
# END LING IELTS FEES GUIDE
'''
new_hooks = hooks_text
if marker not in hooks_text and hook_path not in hooks_text:
    new_hooks = hooks_text + snippet
ast.parse(new_hooks)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
backup = bench / "sites/school.localhost/private/code_backups" / f"fees_code_{stamp}"
backup.mkdir(parents=True, exist_ok=False)
shutil.copy2(hooks, backup / "hooks.py")
if module_destination.exists():
    shutil.copy2(module_destination, backup / "ling_fees.py")

shutil.copy2(module_source, module_destination)
hooks.write_text(new_hooks, encoding="utf-8")
print(f"Đã cài {module_destination}")
print(f"Đã đăng ký hook kiểm tra học phí cho Student Group. Bản sao mã trước thay đổi: {backup}")
print("Tiếp theo chạy bench clear-cache, restart frappe và tạo Client Script theo README.")
