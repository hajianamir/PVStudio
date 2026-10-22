import os
import re

SPECS_DIR = "docs/specs"
PROHIBITED_WORDS = [
    "seamless", "cutting-edge", "world-class", "best-in-class",
    "revolutionary", "state-of-the-art", "powerful", "intuitive"
]

def audit_marketing_language():
    hits = {}
    for root, dirs, files in os.walk(SPECS_DIR):
        for file in files:
            if file.endswith(".md"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                for word in PROHIBITED_WORDS:
                    matches = re.findall(rf"\b{word}\b", content, re.IGNORECASE)
                    if matches:
                        if path not in hits:
                            hits[path] = []
                        hits[path].append((word, len(matches)))
    return hits

if __name__ == "__main__":
    hits = audit_marketing_language()
    if hits:
        print("Marketing language hits found:")
        for path, details in hits.items():
            print(f"  {path}: {details}")
    else:
        print("Clean! No marketing language found.")
