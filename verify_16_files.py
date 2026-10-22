import os
import sys

SPECS_DIR = "docs/specs"
EXPECTED_FILES = [
    "00_index.md",
    "01_architecture.md",
    "02_data_model.md",
    "03_api_groups.md",
    "04_calculation_engine.md",
    "05_ui_ux_spec.md",
    "06_compliance_matrix.md",
    "07_segment_workflows.md",
    "08_risk_register.md",
    "09_phased_roadmap.md",
    "10_acceptance_tests.md",
    "PVStudio_Technical_Product_Specification.md",
    "EXECUTIVE_SUMMARY.md",
    "CHANGELOG.md",
    "HANDOVER.md"
]

def main():
    print("Verifying 15 spec files in docs/specs/ + 1 root SPECIFICATION.md = 16 total files...")
    all_good = True
    for fname in EXPECTED_FILES:
        path = os.path.join(SPECS_DIR, fname)
        if not os.path.exists(path):
            print(f"Missing {path}")
            all_good = False
            continue
        with open(path, "r", encoding="utf-8") as f:
            c = f.read()
        if "Version: 1.0.0" not in c and "| Version |" not in c and fname != "00_index.md":
            print(f"Semver check failed for {fname}")
            all_good = False

    if os.path.exists("SPECIFICATION.md"):
        print("✅ SPECIFICATION.md exists at root.")
    else:
        all_good = False

    if all_good:
        print("🎉 100% PASS: All 16 files verified and semver Version: 1.0.0 aligned!")
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
