#!/usr/bin/env python
import sys

sys.path.insert(0, "src")

from pathlib import Path
from markdown_generator import ObsidianMarkdownGenerator

def main():
    # Load current output
    output_file = Path("output/testcases.md")
    with open(output_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Extract current title line
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("# ") and "FUGUE" in line:
            print("Current title from output:")
            print(line)
            break
    
    print("\nExpected title from references.md:")
    print("# ### THE ART OF FUGUE")

if __name__ == "__main__":
    main()
