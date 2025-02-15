#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path


def lint_files():
    root_dir = Path(__file__).parent.parent
    python_files = list(root_dir.rglob("*.py"))

    print("\n🔍 Found Python files:")
    for file in python_files:
        print(f"  • {file.relative_to(root_dir)}")

    print("\n🔎 Running Ruff linting...")
    try:
        result = subprocess.run(
            ["ruff", "check", *[str(f) for f in python_files]],
            check=True,
            capture_output=True,
            text=True,
        )
        print("✅ Linting complete!")
        print("\nDetailed Results:")
        print("=" * 80)
        print(result.stdout)
        if result.stdout.strip():
            print("\nSummary:")
            summary_lines = [
                line for line in result.stdout.split("\n") if "Found" in line
            ]
            if summary_lines:
                print(summary_lines[-1])
        print("=" * 80)
        return 0
    except subprocess.CalledProcessError as e:
        print("❌ Linting failed!")
        print("\nDetailed Errors:")
        print("=" * 80)
        print(e.stdout)
        print("\nError Output:")
        print(e.stderr)
        print("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(lint_files())
