#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path


def format_files():
    root_dir = Path(__file__).parent.parent
    python_files = list(root_dir.rglob("*.py"))

    print("\n🔍 Found Python files:")
    for file in python_files:
        print(f"  • {file.relative_to(root_dir)}")

    print("\n🎨 Formatting with Ruff...")
    try:
        subprocess.run(
            ["ruff", "format", *[str(f) for f in python_files]],
            check=True,
            capture_output=True,
        )
        print("✨ Formatting complete!")
        return 0
    except subprocess.CalledProcessError as e:
        print("❌ Formatting failed!")
        print(e.stderr.decode())
        return 1


if __name__ == "__main__":
    sys.exit(format_files())
