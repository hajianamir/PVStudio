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
    "HANDOVER.md",
    "PHASE_1_RESIDENTIAL_MVP.md"
]

def check_file(filename):
    path = os.path.join(SPECS_DIR, filename)
    if not os.path.exists(path):
        print(f"❌ Missing: {path}")
        return False
    with open(path, "r", encoding="utf-8") as f:
        c = f.read()
    if "Version: 1.0.0" not in c and "| Version |" not in c and filename != "00_index.md":
        print(f"❌ Version check failed: {filename}")
        return False
    print(f"✅ Verified {filename}")
    return True

def main():
    print("--- Final Verification Pass (16 files in docs/specs/ + 1 root SPECIFICATION.md) ---")
    all_ok = True
    for f in EXPECTED_FILES:
        if not check_file(f):
            all_ok = False

    if os.path.exists("SPECIFICATION.md"):
        print("✅ SPECIFICATION.md exists at root")
    else:
        print("❌ Missing SPECIFICATION.md")
        all_ok = False

    if all_ok:
        print("\n🎉 100% PASS! All 17 documentation artifacts verified.")
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
