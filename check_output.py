import sys
sys.path.insert(0, "src")
from main import process_booklet

result = process_booklet("testcases", "output_test", verbose=False)
print(f"Generated: {result}")
