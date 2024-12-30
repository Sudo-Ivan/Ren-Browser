#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path
import os


def scan_files():
    root_dir = Path(__file__).parent.parent
    python_files = list(root_dir.rglob("*.py"))

    # Validate paths are within project directory
    for file in python_files:
        try:
            if not file.is_relative_to(root_dir):
                print(f"❌ Invalid file path: {file}")
                return 1
        except ValueError as e:
            print(f"❌ Path validation error: {e}")
            return 1

    print("\n🔍 Found Python files:")
    for file in python_files:
        print(f"  • {file.relative_to(root_dir)}")

    print("\n🔒 Running Bandit security scan...")
    try:
        # Use bandit configuration from pyproject.toml
        config_path = root_dir / "pyproject.toml"

        cmd = [
            "bandit",
            "-c",
            str(config_path),  # Use config file
            "-r",  # Recursive
            "-ll",  # Log level low
            "-ii",  # Show info about skipped tests
            "-f",
            "txt",  # Output format
        ]
        cmd.extend(str(f) for f in python_files)

        # Run in a controlled environment
        env = os.environ.copy()
        env["PYTHONPATH"] = str(root_dir)

        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True, env=env, cwd=str(root_dir)
        )

        print("✅ Security scan complete!")
        print("\nDetailed Results:")
        print("=" * 80)
        print(result.stdout)

        if result.stdout.strip():
            print("\nSummary:")
            summary_lines = [
                line
                for line in result.stdout.split("\n")
                if any(
                    x in line
                    for x in ["Run metrics:", "Total issues:", "Files skipped:"]
                )
            ]
            if summary_lines:
                for line in summary_lines:
                    print(line)
        print("=" * 80)
        return 0

    except subprocess.CalledProcessError as e:
        print("❌ Security scan failed!")
        print("\nDetailed Errors:")
        print("=" * 80)
        print(e.stdout)
        print("\nError Output:")
        print(e.stderr)
        print("=" * 80)
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(scan_files())
