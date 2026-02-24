import re
from pathlib import Path

def load_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

ref = load_file('references.md')
out = load_file('output_rapidocr/testcases.md')

print("=== REFERENCE (references.md) ===")
ref_tracks = []
for line in ref.split('\n'):
    if re.match(r'^\d+\s+(Contrapunctus|Canon)', line):
        ref_tracks.append(line.strip())

for t in ref_tracks:
    print(t)

print(f"\nTotal: {len(ref_tracks)} tracks\n")

print("=== RAPIDOCR OUTPUT ===")
out_lines = []
for i, line in enumerate(out.split('\n'), 1):
    if 'Contrapunctus' in line or 'Canon' in line:
        if line.strip():
            out_lines.append(line.strip()[3:].strip() if line.startswith('#') else line.strip())
            
for t in out_lines:
    print(t)

print(f"\nTotal: {len(out_lines)} track lines")

print("\n=== DIFFERENCES ===")
ref_set = [r.lower() for r in ref_tracks]
for o in out_lines:
    o_clean = re.sub(r'[\[\]\(\)]{2,}', '', o).lower()
    if not any(r in o_clean or o_clean in r for r in ref_set):
        print(f"MISMATCH: {o}")
