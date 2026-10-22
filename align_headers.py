import os
import re

SPECS_DIR = "docs/specs"
files = [f for f in os.listdir(SPECS_DIR) if f.endswith(".md")]
files.append("SPECIFICATION.md")

for fname in files:
    path = fname if fname == "SPECIFICATION.md" else os.path.join(SPECS_DIR, fname)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # Replace Version: 1.0 with Version: 1.0.0 in blockquotes
        new_content = content.replace("Version: 1.0\n", "Version: 1.0.0\n")

        if new_content != content:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Updated header semver block in {path}")

print("Header blockquote semver alignment complete!")
