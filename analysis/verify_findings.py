"""Execute isolated controller logic against document ACs, without changing a site."""
import ast
import json
from pathlib import Path
from types import SimpleNamespace

root = Path(__file__).resolve().parent.parent
source = root / 'analysis/basecode/source/education/education/education'

def extract_function(path, name, globals_):
    tree = ast.parse(path.read_text(encoding='utf-8'))
    function = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name)
    function.decorator_list = []
    module = ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[]))
    exec(compile(module, str(path), 'exec'), globals_)
    return globals_[name]

def throw(message):
    raise ValueError(message)

validate = extract_function(source / 'doctype/level_transfer_request/level_transfer_request.py', 'validate',
                            {'frappe': SimpleNamespace(throw=throw), '_': lambda text: text})
checks = []
for remaining, expected in ((12, 750000), (6, 375000)):
    doc = SimpleNamespace(total_sessions=24, remaining_sessions=remaining, current_fee=4000000, new_fee=5500000)
    validate(doc)
    checks.append({'case': f'AC-13 remaining={remaining}', 'expected': expected,
                   'actual': doc.additional_fee, 'passed': expected == doc.additional_fee})
for label, total, remaining, old_fee, new_fee in (
    ('negative remaining', 24, -1, 4000000, 5500000),
    ('remaining exceeds total', 24, 25, 4000000, 5500000),
    ('lower tuition', 24, 12, 5500000, 4000000),
):
    doc = SimpleNamespace(total_sessions=total, remaining_sessions=remaining, current_fee=old_fee, new_fee=new_fee)
    try:
        validate(doc)
        rejected = False
    except ValueError:
        rejected = True
    checks.append({'case': label, 'expected': 'reject', 'actual': 'reject' if rejected else 'allow', 'passed': rejected})

class Expression:
    def __init__(self, fn): self.fn = fn
    def __and__(self, other): return Expression(lambda row: self.fn(row) and other.fn(row))
    def __or__(self, other): return Expression(lambda row: self.fn(row) or other.fn(row))

class Field:
    def __init__(self, name): self.name = name
    def __eq__(self, value): return Expression(lambda row: row[self.name] == value)
    def __ne__(self, value): return Expression(lambda row: row[self.name] != value)
    def __gt__(self, value): return Expression(lambda row: row[self.name] > value)
    def __lt__(self, value): return Expression(lambda row: row[self.name] < value)

class Table:
    def __getattr__(self, name): return Field(name)
    def __getitem__(self, name): return Field(name)

class Query:
    def __init__(self, row): self.row = row
    def select(self, *fields): return self
    def where(self, condition): self.condition = condition; return self
    def run(self, **kwargs): return [SimpleNamespace(**self.row)] if self.condition.fn(self.row) else []

row = {'name': 'existing', 'instructor': 'I-1', 'schedule_date': '2026-11-08', 'docstatus': 0,
       'from_time': 18, 'to_time': 20}
qb = SimpleNamespace(DocType=lambda name: Table(), from_=lambda table: Query(row))
overlap = extract_function(source / 'utils.py', 'get_overlap_for', {'frappe': SimpleNamespace(qb=qb)})
for start, end in ((18, 20), (19, 21), (20, 22), (18, 19), (17, 19), (17, 21), (19, 20)):
    values = {'instructor': 'I-1'}
    doc = SimpleNamespace(from_time=start, to_time=end, schedule_date='2026-11-08', name='new', get=values.get)
    expected = row['from_time'] < end and start < row['to_time']
    actual = overlap(doc, 'Course Schedule', 'instructor') is not None
    checks.append({'case': f'overlap existing=[18,20), new=[{start},{end})',
                   'expected': expected, 'actual': actual, 'passed': expected == actual})

result = {'method': 'Isolated execution of captured controller functions; a small in-memory query-builder adapter evaluates predicates. No live database writes and no end-to-end UAT.',
          'checks': checks, 'passed': sum(c['passed'] for c in checks), 'failed': sum(not c['passed'] for c in checks)}
(root/'analysis/checks.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(result, ensure_ascii=False, indent=2))
