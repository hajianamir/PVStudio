import pytest
import sys

def main():
    print("Running pytest suite for Sprint 1 Evidence Package...")
    ret = pytest.main(["-v", "tests/"])
    if ret == 0:
        print("\n🎉 ALL TESTS PASSED CLEANLY!")
        sys.exit(0)
    else:
        print(f"\n❌ Pytest failed with exit code {ret}")
        sys.exit(ret)

if __name__ == "__main__":
    main()
