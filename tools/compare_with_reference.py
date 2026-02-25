#!/usr/bin/env python

import re
from pathlib import Path

def load_reference():
    ref_path = Path(__file__).parent.parent / "references.md"
    with open(ref_path, "r", encoding="utf-8") as f:
        return f.read()

def parse_reference_tracks(reference_content):
    tracks = []
    for line in reference_content.split("\n"):
        if "THE ART OF FUGUE" in line and "BWV" in line:
            continue
        track_match = re.match(r"^\s*(\d+)\s+(.+)\{(\d+):(\d+)\}", line)
        if track_match:
            track_num = track_match.group(1)
            title = track_match.group(2).strip()
            mins = track_match.group(3)
            secs = track_match.group(4)
            tracks.append(f"{track_num} {title} {{{mins}:{secs}}}")
        elif re.match(r"^\d+\s+", line):
            tracks.append(line.strip())
    return tracks

if __name__ == "__main__":
    reference = load_reference()
    ref_tracks = parse_reference_tracks(reference)
    print("Reference tracks from references.md:")
    for track in ref_tracks:
        print(track)
    if len(ref_tracks) == 20:
        print("\n[OK] All 20 tracks parsed correctly")
